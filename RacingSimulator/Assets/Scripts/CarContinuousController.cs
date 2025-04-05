using System;
using System.Collections.Generic;
using System.Net.Sockets;
using TMPro;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;
using Unity.MLAgents.Sensors;
using UnityEngine;
using UnityEngine.UI;
using Random = UnityEngine.Random;

public class CarContinuousController : Agent
{
    public RawImage carVisionImage;
    public CarController carController;
    public Camera carVisionCamera;
    public GameObject canvas;
    public Transform startPosition;
    public TrackDropDown trackDropDown;
    public BehaviorParameters  behaviorParameters;
    public Raycast Raycast;
    
    private readonly Dictionary<string, Func<float, string>> _floatActions;
    private readonly Dictionary<string, Func<string>> _voidActions;
    private bool _isRunning;
    private RenderTexture _renderTexture;
    private TcpListener _server;
    private TextMeshProUGUI _textMesh;
    private GameObject _textMeshGo;
    private float _timer;
    private readonly List<string> _touchedCheckpoints = new();
    public bool resetCarPosition { get; set; } = false;

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
        _renderTexture = new RenderTexture(347, 256, 1)
        {
            name = CarIndex.ToString()
        };
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
        if (transform.position.y < -20)
        {
            resetCarPosition = true;
            EndEpisode();
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Lines"))
        {
            resetCarPosition = true;
            EndEpisode();
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
                EndEpisode();
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
        _timer = 0f;
        _touchedCheckpoints.Clear();
        if (resetCarPosition)
            ResetCarPosition();
    }
    
    public override void CollectObservations(VectorSensor sensor)
    {
        (List<int> distance, Texture2D newTexture) = Raycast.GetRaycasts(carVisionCamera.targetTexture, carVisionImage.texture as Texture2D, NbRay, Fov);
        
        carVisionImage.texture = newTexture;

        foreach (int i in distance)
        {
            sensor.AddObservation(i);
        }

        for (int i = distance.Count; i < behaviorParameters.BrainParameters.VectorObservationSize - 5; i++)
        {
            sensor.AddObservation(-1);
        }
        sensor.AddObservation(carController.Speed());
        sensor.AddObservation(carController.Steering());
        sensor.AddObservation(carController.transform.position.x);
        sensor.AddObservation(carController.transform.position.y);
        sensor.AddObservation(carController.transform.position.z);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        // var continuousActions = actionsOut.ContinuousActions;

        // continuousActions[0] = Input.GetAxis("Vertical");
        // continuousActions[1] = Input.GetAxis("Horizontal");
    }
}