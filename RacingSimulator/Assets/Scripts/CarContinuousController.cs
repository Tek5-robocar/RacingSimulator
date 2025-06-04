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
    public BehaviorParameters behaviorParameters;
    public Raycast Raycast;

    private readonly Dictionary<string, Func<float, string>> _floatActions;
    private readonly List<string> _touchedCheckpoints = new();
    private readonly Dictionary<string, Func<string>> _voidActions;
    private bool _isRunning;
    private RenderTexture _renderTexture;
    private TcpListener _server;
    private TextMeshProUGUI _textMesh;
    private GameObject _textMeshGo;
    private float _timer;
    public bool resetCarPosition { get; set; }

    public float AlignmentScale { get; set; }
    public float SignedDistanceToCenterScale { get; set; }
    public float SpeedScale { get; set; }

    public int NumberCollider { get; set; }
    public float Fov { get; set; }

    public int NbRay { get; set; }
    public CentralLine CentralLine { get; set; }

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
                var minutes = Mathf.FloorToInt(_timer / 60);
                var seconds = Mathf.FloorToInt(_timer % 60);
                Debug.Log($"you finished a lap in {minutes:00}:{seconds:00} !!");
                trackDropDown.UpdateBestScore(_timer);
                EndEpisode();
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
        _textMesh.text =
            string.Format($"Agent {CarIndex}: {Mathf.FloorToInt(_timer / 60):00}:{Mathf.FloorToInt(_timer % 60):00}");
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

    private float ComputeSignedDistanceToCenterReward()
{
    // Get the car's position
    Vector3 carPosition = transform.position;

    // Initialize variables to find the closest point on the LineRenderer
    float minDistance = float.MaxValue;
    Vector3 closestPoint = Vector3.zero;
    Vector3 segmentDirection = Vector3.zero;

    // Iterate through each segment of the LineRenderer
    for (int i = 0; i < CentralLine.fullCentralLine.Count - 1; i++)
    {
        Vector3 pointA = CentralLine.fullCentralLine[i];
        Vector3 pointB = CentralLine.fullCentralLine[i + 1];

        // Find the closest point on the segment from pointA to pointB
        Vector3 pointOnSegment = ClosestPointOnLineSegment(carPosition, pointA, pointB);

        // Calculate the distance to this point
        float distance = Vector3.Distance(carPosition, pointOnSegment);

        // Update the closest point if this distance is smaller
        if (distance < minDistance)
        {
            minDistance = distance;
            closestPoint = pointOnSegment;
            segmentDirection = (pointB - pointA).normalized;
        }
    }

    // Calculate the signed distance
    // Use the cross product to determine if the car is to the left or right of the line
    Vector3 carToClosest = carPosition - closestPoint;
    Vector3 lineUp = Vector3.up; // Assuming the track is in the XZ plane
    Vector3 cross = Vector3.Cross(segmentDirection, carToClosest);
    float signedDistance = minDistance * Mathf.Sign(Vector3.Dot(cross, lineUp));

    // Normalize the reward (e.g., penalize larger distances)
    // You can adjust the denominator based on the track's scale
    float maxDistance = 10f; // Maximum relevant distance (adjust as needed)
    float reward = 1f - Mathf.Abs(signedDistance) / maxDistance;
    reward = Mathf.Clamp(reward, -1f, 1f); // Ensure reward is within [-1, 1]

    return reward;
}

private float ComputeAlignmentWithCenterReward()
{
    // Get the car's forward direction
    Vector3 carForward = transform.forward;

    // Initialize variables to find the closest point and segment direction
    Vector3 closestPoint = Vector3.zero;
    Vector3 segmentDirection = Vector3.zero;
    float minDistance = float.MaxValue;

    // Iterate through each segment to find the closest point and its direction
    for (int i = 0; i < CentralLine.fullCentralLine.Count - 1; i++)
    {
        Vector3 pointA = CentralLine.fullCentralLine[i];
        Vector3 pointB = CentralLine.fullCentralLine[i + 1];

        // Find the closest point on the segment
        Vector3 pointOnSegment = ClosestPointOnLineSegment(transform.position, pointA, pointB);

        // Calculate the distance to this point
        float distance = Vector3.Distance(transform.position, pointOnSegment);

        // Update the closest point and direction if this distance is smaller
        if (distance < minDistance)
        {
            minDistance = distance;
            closestPoint = pointOnSegment;
            segmentDirection = (pointB - pointA).normalized;
        }
    }

    // Calculate the alignment using the dot product between car's forward and line's tangent
    float alignment = Vector3.Dot(carForward.normalized, segmentDirection);
    // The dot product ranges from -1 (opposite direction) to 1 (same direction)
    // We want to reward positive alignment and penalize negative alignment
    float reward = alignment; // Already in [-1, 1]

    return reward;
}

// Helper function to find the closest point on a line segment
private Vector3 ClosestPointOnLineSegment(Vector3 point, Vector3 segmentStart, Vector3 segmentEnd)
{
    Vector3 segment = segmentEnd - segmentStart;
    float segmentLengthSqr = segment.sqrMagnitude;

    // If the segment has no length, return the start point
    if (segmentLengthSqr == 0f)
        return segmentStart;

    // Project the point onto the line segment
    float t = Vector3.Dot(point - segmentStart, segment) / segmentLengthSqr;
    t = Mathf.Clamp01(t); // Clamp to the segment

    return segmentStart + t * segment;
}

    private float ComputeSpeedReward()
    {
        return carController.Speed() / carController.maxSpeed;
    }

    private void SetRewards()
    {
        var alignmentReward = ComputeAlignmentWithCenterReward() * AlignmentScale;
        var signedDistanceToCenterReward = ComputeSignedDistanceToCenterReward() * SignedDistanceToCenterScale;
        var speedReward = ComputeSpeedReward() * SpeedScale;
        var reward = alignmentReward + signedDistanceToCenterReward + speedReward;
        AddReward(reward);
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        SetRewards();

        var (distance, newTexture) = Raycast.GetRaycasts(carVisionCamera.targetTexture,
            carVisionImage.texture as Texture2D, NbRay, Fov);

        carVisionImage.texture = newTexture;

        foreach (var i in distance) sensor.AddObservation(i);

        for (var i = distance.Count; i < behaviorParameters.BrainParameters.VectorObservationSize - 5; i++)
            sensor.AddObservation(-1);
        sensor.AddObservation(carController.Speed());
        sensor.AddObservation(carController.Steering());
        sensor.AddObservation(carController.transform.position.x);
        sensor.AddObservation(carController.transform.position.y);
        sensor.AddObservation(carController.transform.position.z);
    }

    public override void Heuristic(in ActionBuffers actionsOut)
    {
        var continuousActions = actionsOut.ContinuousActions;

        continuousActions[0] = Input.GetAxis("Vertical");
        continuousActions[1] = Input.GetAxis("Horizontal");
    }
}