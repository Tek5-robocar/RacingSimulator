using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Random = UnityEngine.Random;

public class TcpServer : MonoBehaviour
{
    public GameObject agents;
    public GameObject agentPrefab;
    public ViewDropDown viewDropDown;
    public Transform startPosition;
    public GameObject canvas;

    private int port = 8085;
    private readonly ConcurrentQueue<TcpClient> addClientQueue = new();
    private readonly List<(TcpClient, CarServerController)> connectedClients = new();
    private readonly string folderPath = Path.Combine("CarMaterialVariation");
    private readonly ConcurrentQueue<(TcpClient, string)> messageQueue = new();
    private readonly ConcurrentQueue<TcpClient> removeClientQueue = new();
    private readonly ConcurrentQueue<(TcpClient, string)> responseQueue = new();
    private Thread broadcastThread;
    // private bool isBroadcasting = true;
    private bool isServerRunning;
    private Material[] materials;
    private TcpListener tcpListener;

    private void Start()
    {
        StartServer();
        materials = Resources.LoadAll<Material>(folderPath);
        // StartBroadcastThread();
    }

    private void Update()
    {
        while (addClientQueue.Count > 0)
            if (addClientQueue.TryDequeue(out var tcpClient))
                AddClient(tcpClient);

        while (removeClientQueue.Count > 0)
            if (removeClientQueue.TryDequeue(out var client))
                RemoveClient(client);

        while (messageQueue.Count > 0)
            if (messageQueue.TryDequeue(out var message))
            {
                var (_, carServerController) = connectedClients.Find(tuple => tuple.Item1 == message.Item1);
                var response = carServerController.HandleClientCommand(message.Item2);
                responseQueue.Enqueue((message.Item1, response));
            }

        while (responseQueue.Count > 0)
            if (responseQueue.TryDequeue(out var response))
                if (response.Item1 != null)
                    BroadcastMessage(response.Item2, response.Item1);
    }

    private void OnApplicationQuit()
    {
        // isBroadcasting = false;
        if (broadcastThread != null && broadcastThread.IsAlive) broadcastThread.Join();

        if (isServerRunning)
        {
            tcpListener.Stop();
            Debug.Log("TCP Server stopped.");
        }

        foreach (var (client, _) in connectedClients)
        {
            Debug.Log("Closing client connection: " + client.Client.RemoteEndPoint);
            client.Close();
        }
    }

    private void AddClient(TcpClient tcpClient)
    {
        var newGo = Instantiate(agentPrefab, agents.transform, true);
        newGo.transform.position = startPosition.position;
        if (materials.Length > 0)
            for (var i = 0; i < newGo.transform.childCount; i++)
                if (newGo.transform.GetChild(i).name == "Body")
                {
                    var randomMaterial = materials[Random.Range(0, materials.Length)];
                    var tempMaterials = newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials;
                    tempMaterials[0] = randomMaterial;
                    newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials = tempMaterials;
                }

        var carsController = newGo.GetComponent<CarServerController>();
        carsController.CarIndex = connectedClients.Count;
        carsController.canvas = canvas;
        carsController.startPosition = startPosition;
        connectedClients.Add((tcpClient, carsController));
        for (var i = 0; i < newGo.transform.childCount; i++)
            foreach (var myCamera in newGo.transform.GetChild(i).GetComponents<Camera>())
                viewDropDown.AddCamera(myCamera, carsController.CarIndex);
    }

    private void StartServer()
    {
        try
        {
            tcpListener = new TcpListener(IPAddress.Loopback, port);
            tcpListener.Start();
            isServerRunning = true;
            Debug.Log("TCP Server started, waiting for connections...");

            tcpListener.BeginAcceptTcpClient(OnClientConnected, null);
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
            var tcpClient = tcpListener.EndAcceptTcpClient(result);
            Debug.Log("Client connected from: " + tcpClient.Client.RemoteEndPoint);

            addClientQueue.Enqueue(tcpClient);

            var networkStream = tcpClient.GetStream();
            var buffer = new byte[1024];
            networkStream.BeginRead(buffer, 0, buffer.Length, OnDataReceived, new ConnectionState(tcpClient, buffer));

            tcpListener.BeginAcceptTcpClient(OnClientConnected, null);
        }
        catch (Exception ex)
        {
            if (tcpListener.Pending())
                Debug.LogError("Error handling client connection: " + ex.Message);
        }
    }

    private void OnDataReceived(IAsyncResult result)
    {
        var state = (ConnectionState)result.AsyncState;
        var tcpClient = state.TcpClient;
        try
        {
            var buffer = state.Buffer;

            var networkStream = tcpClient.GetStream();
            var bytesRead = networkStream.EndRead(result);

            if (bytesRead > 0)
            {
                var message = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                messageQueue.Enqueue((tcpClient, message));

                networkStream.BeginRead(buffer, 0, buffer.Length, OnDataReceived, state);
            }
            else
            {
                Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
                tcpClient.Close();
                removeClientQueue.Enqueue(tcpClient);
            }
        }
        catch (Exception ex)
        {
            Debug.LogError("Error receiving data: " + ex.Message);
            Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
            tcpClient.Close();
            removeClientQueue.Enqueue(tcpClient);
        }
    }

    public void BroadcastMessage(string message, TcpClient tcpClient)
    {
        var data = Encoding.ASCII.GetBytes(message);

        try
        {
            var stream = tcpClient.GetStream();
            if (stream.CanWrite) stream.Write(data, 0, data.Length);
        }
        catch (Exception ex)
        {
            Debug.LogError("Error sending message to tcpClient: " + ex.Message);
            removeClientQueue.Enqueue(tcpClient);

            tcpClient.Close();
        }
    }

    public void BroadcastMessageEveryone(string message)
    {
        for (var i = connectedClients.Count - 1; i >= 0; i--)
        {
            var client = connectedClients[i].Item1;
            BroadcastMessage(message, client);
        }
    }

    private void RemoveClient(TcpClient tcpClient)
    {
        var client = connectedClients.Find(client => client.Item1 == tcpClient);
        if (client == default((TcpClient, CarServerController))) return;

        var go = client.Item2.gameObject;
        for (var i = 0; i < go.transform.childCount; i++)
            foreach (var myCamera in go.transform.GetChild(i).GetComponents<Camera>())
                viewDropDown.RemoveCamera(myCamera, client.Item2.CarIndex);
        connectedClients.RemoveAt(connectedClients.FindIndex(tuple => tuple.Item1 == tcpClient));
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