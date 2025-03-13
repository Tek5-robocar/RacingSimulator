using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using TMPro;
using UnityEngine;
using Random = UnityEngine.Random;

public class TcpServer : MonoBehaviour
{
    public GameObject agents;
    public GameObject agentPrefab;
    public ViewDropDown viewDropDown;
    public TrackDropDown trackDropDown;
    public Transform startPosition;
    public GameObject canvas;
    public LapManager lapManager;
    
    private readonly ConcurrentQueue<TcpClient> _addClientQueue = new();
    private readonly List<(TcpClient, CarServerController)> _connectedClients = new();
    private readonly string _folderPath = Path.Combine("CarMaterialVariation");
    private readonly ConcurrentQueue<(TcpClient, string)> _messageQueue = new();

    private const int Port = 8085;
    private readonly ConcurrentQueue<TcpClient> _removeClientQueue = new();
    private readonly ConcurrentQueue<(TcpClient, string)> _responseQueue = new();

    private Thread _broadcastThread;

    private bool _isServerRunning;
    private Material[] _materials;
    private TcpListener _tcpListener;
    private readonly Dictionary<TcpClient, CarServerController> _clientDictionary = new();

    private void Start()
    {
        StartServer();
        _materials = Resources.LoadAll<Material>(_folderPath);
    }

    private void Update()
    {
        while (_addClientQueue.Count > 0)
            if (_addClientQueue.TryDequeue(out TcpClient tcpClient))
                AddClient(tcpClient);

        while (_removeClientQueue.Count > 0)
            if (_removeClientQueue.TryDequeue(out TcpClient client))
                RemoveClient(client);

        while (_messageQueue.Count > 0)
            if (_messageQueue.TryDequeue(out (TcpClient, string) message))
            {
                (_, CarServerController carServerController) = _connectedClients.Find(tuple => tuple.Item1 == message.Item1);
                // if (_clientDictionary.TryGetValue(message.Item1, out CarServerController carServerController))
                // {
                    // string response = carServerController.HandleClientCommand(message.Item2);
                    // _responseQueue.Enqueue((message.Item1, response));
                // }

                string response = carServerController.HandleClientCommand(message.Item2);
                _responseQueue.Enqueue((message.Item1, response));
            }

        while (_responseQueue.Count > 0)
            if (_responseQueue.TryDequeue(out (TcpClient, string) response))
                if (response.Item1 != null)
                    BroadcastMessage(response.Item2, response.Item1);
    }

    private void OnApplicationQuit()
    {
        if (_broadcastThread != null && _broadcastThread.IsAlive) _broadcastThread.Join();

        if (_isServerRunning)
        {
            _tcpListener.Stop();
            Debug.Log("TCP Server stopped.");
        }

        foreach ((TcpClient client, CarServerController _) in _connectedClients)
        {
            Debug.Log("Closing client connection: " + client.Client.RemoteEndPoint);
            client.Close();
        }
    }

    private List<(TcpClient, string)> GroupResponseByClient()
    {
        List<(TcpClient, string)> groupedResponses = new();
        while (_responseQueue.TryDequeue(out (TcpClient, string) response))
        {
            (TcpClient, string) groupedResponse = groupedResponses.Find(x => x.Item1 == response.Item1);
            if (groupedResponse != default((TcpClient, string)))
                groupedResponse.Item2 += ";" + response.Item2;
            else
                groupedResponses.Add(response);
        }

        return groupedResponses;
    }

    private void AddClient(TcpClient tcpClient)
    {
        GameObject newGo = Instantiate(agentPrefab, agents.transform, true);
        newGo.transform.position = startPosition.position;
        if (_materials.Length > 0)
            for (int i = 0; i < newGo.transform.childCount; i++)
                if (newGo.transform.GetChild(i).name == "Body")
                {
                    Material randomMaterial = _materials[Random.Range(0, _materials.Length)];
                    Material[] tempMaterials = newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials;
                    tempMaterials[0] = randomMaterial;
                    newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials = tempMaterials;
                }

        CarServerController carsController = newGo.GetComponent<CarServerController>();
        carsController.CarIndex = _connectedClients.Count;
        carsController.canvas = canvas;
        carsController.startPosition = startPosition;
        carsController.trackDropDown = trackDropDown; 
        _connectedClients.Add((tcpClient, carsController));
        for (int i = 0; i < newGo.transform.childCount; i++)
            foreach (Camera myCamera in newGo.transform.GetChild(i).GetComponents<Camera>())
                viewDropDown.AddCamera(myCamera, carsController.CarIndex);

        lapManager.AddCar(newGo);
    }

    private void StartServer()
    {
        try
        {
            _tcpListener = new TcpListener(IPAddress.Loopback, Port);
            _tcpListener.Start();
            _isServerRunning = true;
            Debug.Log("TCP Server started, waiting for connections...");

            _tcpListener.BeginAcceptTcpClient(OnClientConnected, null);
        }
        catch (Exception ex)
        {
            Debug.LogError("Error starting server: " + ex.Message);
        }
    }

    private void OnClientConnected(IAsyncResult result)
    {
        try
        {
            TcpClient tcpClient = _tcpListener.EndAcceptTcpClient(result);
            Debug.Log("Client connected from: " + tcpClient.Client.RemoteEndPoint);

            _addClientQueue.Enqueue(tcpClient);

            NetworkStream networkStream = tcpClient.GetStream();
            byte[] buffer = new byte[1024];
            networkStream.BeginRead(buffer, 0, buffer.Length, OnDataReceived, new ConnectionState(tcpClient, buffer));

            _tcpListener.BeginAcceptTcpClient(OnClientConnected, null);
        }
        catch (Exception ex)
        {
            if (_tcpListener.Pending())
                Debug.LogError("Error handling client connection: " + ex.Message);
        }
    }

    private void OnDataReceived(IAsyncResult result)
    {
        ConnectionState state = (ConnectionState)result.AsyncState;
        TcpClient tcpClient = state.TcpClient;
        try
        {
            byte[] buffer = state.Buffer;

            NetworkStream networkStream = tcpClient.GetStream();
            int bytesRead = networkStream.EndRead(result);

            if (bytesRead > 0)
            {
                string message = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                _messageQueue.Enqueue((tcpClient, message));

                networkStream.BeginRead(buffer, 0, buffer.Length, OnDataReceived, state);
            }
            else
            {
                Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
                tcpClient.Close();
                _removeClientQueue.Enqueue(tcpClient);
            }
        }
        catch (Exception ex)
        {
            Debug.LogError("Error receiving data: " + ex.Message);
            Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
            tcpClient.Close();
            _removeClientQueue.Enqueue(tcpClient);
        }
    }

    public void BroadcastMessage(string message, TcpClient tcpClient)
    {
        byte[] data = Encoding.ASCII.GetBytes(message);

        try
        {
            NetworkStream stream = tcpClient.GetStream();
            if (stream.CanWrite) stream.Write(data, 0, data.Length);
        }
        catch (Exception ex)
        {
            Debug.LogError("Error sending message to tcpClient: " + ex.Message);
            _removeClientQueue.Enqueue(tcpClient);

            tcpClient.Close();
        }
    }

    public void BroadcastMessageEveryone(string message)
    {
        for (int i = _connectedClients.Count - 1; i >= 0; i--)
        {
            TcpClient client = _connectedClients[i].Item1;
            BroadcastMessage(message, client);
        }
    }

    private void RemoveClient(TcpClient tcpClient)
    {
        (TcpClient, CarServerController) client = _connectedClients.Find(client => client.Item1 == tcpClient);
        if (client == default((TcpClient, CarServerController))) return;

        GameObject go = client.Item2.gameObject;
        for (int i = 0; i < go.transform.childCount; i++)
            foreach (Camera myCamera in go.transform.GetChild(i).GetComponents<Camera>())
                viewDropDown.RemoveCamera(myCamera, client.Item2.CarIndex);
        _connectedClients.RemoveAt(_connectedClients.FindIndex(tuple => tuple.Item1 == tcpClient));
        lapManager.RemoveCar(go);
        Destroy(go);
    }

    private class ConnectionState
    {
        public ConnectionState(TcpClient tcpClient, byte[] buffer)
        {
            TcpClient = tcpClient;
            Buffer = buffer;
        }

        public TcpClient TcpClient { get; }
        public byte[] Buffer { get; }
    }
}