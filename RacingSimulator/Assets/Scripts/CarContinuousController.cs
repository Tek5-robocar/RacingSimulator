using System;
using System.Collections.Generic;
using System.Net.Sockets;
using TMPro;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using Random = UnityEngine.Random;

public class CarContinuousController : Agent
{
    public CarController carController;
    public Camera carVisionCamera;
    public GameObject canvas;
    public Transform startPosition;
    public TrackDropDown trackDropDown;
    public BehaviorParameters  behaviorParameters;
    
    private readonly Dictionary<string, Func<float, string>> _floatActions;
    private readonly Dictionary<string, Func<string>> _voidActions;
    private bool _isRunning;
    private RenderTexture _renderTexture;
    private TcpListener _server;
    private TextMeshProUGUI _textMesh;
    private GameObject _textMeshGo;
    private float _timer;
    private readonly List<string> _touchedCheckpoints = new();

    public int NumberCollider { get; set; }
    public float Fov { get; set; }

    public int NbRay { get; set; }

    public int CarIndex
    {
        get => behaviorParameters.TeamId;
        set
        {
            behaviorParameters.BehaviorName += value;
            behaviorParameters.TeamId = value;
        }
    }

    private void Start()
    {
        _renderTexture = new RenderTexture(694 / 2, 512 / 2, 1);
        carVisionCamera.targetTexture = _renderTexture;

        Random.InitState(DateTime.Now.Millisecond);

        _textMeshGo = new GameObject();
        _textMeshGo.transform.SetParent(canvas.transform);
        _textMeshGo.transform.localPosition = new Vector3(247, 230 - 30 * CarIndex, 0);
        _textMesh = _textMeshGo.AddComponent<TextMeshProUGUI>();
        _textMesh.enableAutoSizing = true;
        _textMesh.color = Color.black;
    }

    private void Update()
    {
        UpdateTimer();
    }

    private void FixedUpdate()
    {
        if (transform.position.y < -20) ResetCarPosition();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Lines"))
        {
            ResetCarPosition();
        }
        else if (other.CompareTag("Checkpoint"))
        {
            if (!_touchedCheckpoints.Contains(other.name)) _touchedCheckpoints.Add(other.name);
        }
        else if (other.CompareTag("Finish"))
        {
            if (_touchedCheckpoints.Count == NumberCollider && NumberCollider != 0)
            {
                _timer += Time.deltaTime;
                int minutes = Mathf.FloorToInt(_timer / 60);
                int seconds = Mathf.FloorToInt(_timer % 60);
                Debug.Log($"you finished a lap in {minutes:00}:{seconds:00} !!");
                trackDropDown.UpdateBestScore(_timer);
                _timer = 0f;
            }
            else
            {
            }
            _touchedCheckpoints.Clear();
        }
    }


    ~CarContinuousController()
    {
        Destroy(_textMeshGo);
        Destroy(_textMesh);
    }

    public void ResetCarPosition()
    {
        carController.Reset();
        gameObject.transform.position = startPosition.position;
        gameObject.transform.rotation = startPosition.rotation;
        transform.Rotate(new Vector3(0, -90, 0));
        _touchedCheckpoints.Clear();
        _timer = 0f; 
    }

    private void UpdateTimer()
    {
        _timer += Time.deltaTime;
        _textMesh.text = string.Format($"Agent {CarIndex}: {Mathf.FloorToInt(_timer / 60):00}:{Mathf.FloorToInt(_timer % 60):00}");
    }
    
    public override void OnActionReceived(ActionBuffers actionBuffers)
    {
        var throttle = actionBuffers.ContinuousActions[0];
        var steering = actionBuffers.ContinuousActions[1];
        carController.Move(throttle);
        carController.Turn(steering);
    }

    public override void OnEpisodeBegin()
    {
        ResetCarPosition();
    }
    
    public override void CollectObservations(VectorSensor sensor)
    {
        List<int> distance = RenderTextureToString.GetRaycasts(carVisionCamera.targetTexture, NbRay, Fov);

        foreach (int i in distance)
        {
            sensor.AddObservation(i);
        }

        for (int i = distance.Count; i < behaviorParameters.BrainParameters.VectorObservationSize; i++)
        {
            sensor.AddObservation(-1);
        }
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // var continuousActions = actionsOut.ContinuousActions;

        // continuousActions[0] = Input.GetAxis("Vertical");
        // continuousActions[1] = Input.GetAxis("Horizontal");
    }
}