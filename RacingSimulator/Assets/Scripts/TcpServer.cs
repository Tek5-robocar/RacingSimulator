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
    private const int Port = 8085;
    public GameObject agents;
    public GameObject agentPrefab;
    public ViewDropDown viewDropDown;
    public TrackDropDown trackDropDown;
    public Transform startPosition;
    public GameObject canvas;
    public CentraleLine lapManager;
    
    private Thread _broadcastThread;
    private bool _isServerRunning;
    private Material[] _materials;
    private TcpListener _tcpListener;
    private readonly TcpClient _client;
    // private static int _nbCars = 1;
    // private static int _fov = 110;
    // private static int _nbRay = 10;
    private readonly string _folderPath = Path.Combine("CarMaterialVariation");
    private readonly ConcurrentQueue<Action> _mainThreadActions = new ConcurrentQueue<Action>();
    // private readonly Dictionary<string, Action<string>> _commands = new Dictionary<string, Action<string>>()
    // {
        // {"NB_AGENT", (value) =>
        // {
            // if (int.TryParse(value, out int nbAgent))
            // {
                // if (nbAgent > 0)
                // {
                    // _nbCars = nbAgent;
                // }
            // }
        // }},
        // {"FOV", (value) =>
        // {
            // if (int.TryParse(value, out int fov))
            // {
                // if (fov is > 1 and < 180)
                // {
                    // _fov = fov;
                // }
            // }
        // }},
        // {"NB_RAY", (value) =>
        // {
            // if (int.TryParse(value, out int nbRay))
            // {
                // if (nbRay is > 1 and < 50)
                // {
                    // _nbRay = nbRay;
                // }
            // }
        // }},
    // };

    private AgentsConfig _content;
    

    private void Start()
    {
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = -1;
        StartServer();
        _materials = Resources.LoadAll<Material>(_folderPath);
    }

    private void Update()
    {
        while(_mainThreadActions.TryDequeue(out var action))
            action();
    }

    private void OnApplicationQuit()
    {
        if (_broadcastThread != null && _broadcastThread.IsAlive) _broadcastThread.Join();

        if (_isServerRunning)
        {
            _tcpListener.Stop();
            Debug.Log("TCP Server stopped.");
        }

        Debug.Log("Closing client connection: " + _client.Client.RemoteEndPoint);
        _client.Close();
    }

    private void AddClient(int index)
    {
        var newGo = Instantiate(agentPrefab, agents.transform, true);
        newGo.transform.position = startPosition.position;
        if (_materials.Length > 0)
            for (var i = 0; i < newGo.transform.childCount; i++)
                if (newGo.transform.GetChild(i).name == "Body")
                {
                    var randomMaterial = _materials[Random.Range(0, _materials.Length)];
                    var tempMaterials = newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials;
                    tempMaterials[0] = randomMaterial;
                    newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials = tempMaterials;
                }

        var carsController = newGo.GetComponent<CarContinuousController>();
        Debug.Log($"setting car index to {index}, fov to {_content.agents[index].fov} and nbRay to {_content.agents[index].nbRay}");
        carsController.CarIndex = index;
        carsController.Fov = _content.agents[index].fov;
        carsController.NbRay = _content.agents[index].nbRay;
        carsController.canvas = canvas;
        carsController.startPosition = startPosition;
        carsController.trackDropDown = trackDropDown;
        for (var i = 0; i < newGo.transform.childCount; i++)
            foreach (var myCamera in newGo.transform.GetChild(i).GetComponents<Camera>())
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
            var tcpClient = _tcpListener.EndAcceptTcpClient(result);
            Debug.Log("Client connected from: " + tcpClient.Client.RemoteEndPoint);

            var networkStream = tcpClient.GetStream();
            var buffer = new byte[1024];
            networkStream.BeginRead(buffer, 0, buffer.Length, OnDataReceived, new ConnectionState(tcpClient, buffer));
            _tcpListener.BeginAcceptTcpClient(OnClientConnected, null);
        }
        catch (Exception ex)
        {
            if (_tcpListener.Pending())
                Debug.LogError("Error handling client connection: " + ex.Message);
        }
    }

    [System.Serializable]
    public class AgentConfig
    {
        public int fov;
        public int nbRay;
    }

    [System.Serializable]
    public class AgentsConfig
    {
        public AgentConfig[] agents;
    }

    private bool ExtractInfoFromMessage(string message)
    {
        Debug.Log($"ExtractInfoFromMessage: {message}");
        _content = JsonUtility.FromJson<AgentsConfig>(message);

        foreach (AgentConfig agent in _content.agents)
        {
            if (agent.fov <= 0 || agent.fov > 180 || agent.nbRay <= 0 || agent.nbRay > 50)
            {
                return false;
            }
        }
        return true;
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
                if (!ExtractInfoFromMessage(message))
                {
                    Debug.LogError("wrong message");
                    BroadcastMessage("wrong message", tcpClient);
                } else
                {
                    for (int i = 0; i < _content.agents.Length; i++)
                    {
                        var i1 = i;
                        _mainThreadActions.Enqueue(() => AddClient(i1));
                    }
                }
            }
            else
            {
                Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
                tcpClient.Close();
            }
        }
        catch (Exception ex)
        {
            Debug.LogError("Error receiving data: " + ex.Message);
            Debug.Log("Client disconnected: " + tcpClient.Client.RemoteEndPoint);
            tcpClient.Close();
        }
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