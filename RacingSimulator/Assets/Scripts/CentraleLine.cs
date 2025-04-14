using System.Collections.Generic;
using UnityEngine;

public class CentralLine : MonoBehaviour
{
    private readonly List<GameObject> _cars = new();
    private LineRenderer _centralLine;
    private readonly List<Vector3> _centralPoints = new();

    private int _numberCollider;
    private GameObject _track;

    public void AddCar(GameObject car)
    {
        _cars.Add(car);
        var carController = car.GetComponent<CarContinuousController>();
        carController.NumberCollider = _numberCollider;
    }

    private int GetClosestVectorIndex(Vector3 target, Vector3[] vectors)
    {
        if (vectors == null || vectors.Length == 0)
        {
            Debug.LogError("The vector array is null or empty.");
            return -1;
        }

        var closestIndex = 0;
        var closestDistance = Vector3.Distance(target, vectors[0]);

        for (var i = 1; i < vectors.Length; i++)
        {
            var distance = Vector3.Distance(target, vectors[i]);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestIndex = i;
            }
        }

        return closestIndex;
    }

    private Vector3 RotatePointAroundPivot(Vector3 point, Vector3 pivot, Quaternion rotation)
    {
        var direction = point - pivot;
        direction = rotation * direction;
        return pivot + direction;
    }

    private void GenerateCentralLineRendererPart(GameObject part)
    {
        var lines = part.GetComponentsInChildren<LineRenderer>();
        if (lines.Length != 2) return;
        var associatedPoints = new List<(Vector3, Vector3)>();
        var bigger = new Vector3[lines[0].positionCount > lines[1].positionCount
            ? lines[0].positionCount
            : lines[1].positionCount];
        var smaller = new Vector3[lines[0].positionCount > lines[1].positionCount
            ? lines[1].positionCount
            : lines[0].positionCount];

        if (lines[0].positionCount > lines[1].positionCount)
        {
            lines[0].GetPositions(bigger);
            for (var i = 0; i < bigger.Length; i++)
            {
                bigger[i] += lines[0].transform.position;
                bigger[i] = RotatePointAroundPivot(bigger[i], lines[0].transform.position, lines[0].transform.rotation);
            }

            lines[1].GetPositions(smaller);
            for (var i = 0; i < smaller.Length; i++)
            {
                smaller[i] += lines[1].transform.position;
                smaller[i] =
                    RotatePointAroundPivot(smaller[i], lines[1].transform.position, lines[1].transform.rotation);
            }
        }
        else
        {
            lines[0].GetPositions(smaller);
            for (var i = 0; i < smaller.Length; i++)
            {
                smaller[i] += lines[0].transform.position;
                smaller[i] =
                    RotatePointAroundPivot(smaller[i], lines[0].transform.position, lines[0].transform.rotation);
            }

            lines[1].GetPositions(bigger);
            for (var i = 0; i < bigger.Length; i++)
            {
                bigger[i] += lines[1].transform.position;
                bigger[i] = RotatePointAroundPivot(bigger[i], lines[1].transform.position, lines[1].transform.rotation);
            }
        }

        foreach (var biggerPos in bigger)
        {
            var closestIndex = GetClosestVectorIndex(biggerPos, smaller);
            associatedPoints.Add((biggerPos, smaller[closestIndex]));
        }

        _centralLine = part.AddComponent<LineRenderer>();
        _centralLine.positionCount = associatedPoints.Count;
        _centralLine.widthMultiplier = 0f;

        for (var i = 0; i < associatedPoints.Count; i++)
        {
            var centralPoint = new Vector3(
                (associatedPoints[i].Item1.x + associatedPoints[i].Item2.x) / 2,
                (associatedPoints[i].Item1.y + associatedPoints[i].Item2.y) / 2,
                (associatedPoints[i].Item1.z + associatedPoints[i].Item2.z) / 2
            );
            _centralLine.SetPosition(i, centralPoint);
            _centralPoints.Add(centralPoint);
        }

        var linesColliders = part.AddComponent<LineRendererColliderGenerator>();
        linesColliders.ColliderWidth = 15f;
        linesColliders.ColliderIndexOffset = 5;

        linesColliders.OnStartFinished += () =>
        {
            foreach (var boxCollider in linesColliders.GetColliders())
            {
                _numberCollider++;
                foreach (var car in _cars)
                {
                    var carController = car.GetComponent<CarContinuousController>();
                    carController.NumberCollider = _numberCollider;
                }

                boxCollider.name = $"checkpoint_{_numberCollider}";
                boxCollider.tag = "Checkpoint";
            }
        };
    }

    private void GenerateCentralLineRenderer()
    {
        for (var i = 0; i < _track.transform.childCount; i++)
            GenerateCentralLineRendererPart(_track.transform.GetChild(i).gameObject);
    }

    public void SetTrack(GameObject track)
    {
        _numberCollider = 0;
        foreach (var car in _cars)
        {
            var carController = car.GetComponent<CarContinuousController>();
            carController.NumberCollider = -1;
        }

        _track = track;
        GenerateCentralLineRenderer();
    }

    public void RemoveCar(GameObject car)
    {
        _cars.Remove(car);
    }

    public float SignedDistanceToLine(Vector3 point)
    {
        if (_centralPoints == null || _centralPoints.Count < 2)
        {
            Debug.LogError("Line must have at least 2 points");
            return float.MaxValue;
        }

        var minDistance = float.MaxValue;
        float signedDistance = 0;

        for (var i = 0; i < _centralPoints.Count - 1; i++)
        {
            var a = _centralPoints[i];
            var b = _centralPoints[i + 1];

            var distance = SignedDistanceToSegment(a, b, point, out var currentSign);

            if (Mathf.Abs(distance) < Mathf.Abs(minDistance))
            {
                minDistance = distance;
                signedDistance = distance;
            }
        }

        return signedDistance;
    }

    private static float SignedDistanceToSegment(Vector3 a, Vector3 b, Vector3 point, out float sign)
    {
        var ab = b - a;
        var ap = point - a;

        var projection = Vector3.Dot(ap, ab.normalized);
        var abLength = ab.magnitude;

        Vector3 closestPoint;
        if (projection <= 0)
            closestPoint = a;
        else if (projection >= abLength)
            closestPoint = b;
        else
            closestPoint = a + ab.normalized * projection;

        var distanceVector = point - closestPoint;
        var distance = distanceVector.magnitude;

        var cross = Vector3.Cross(ab.normalized, ap.normalized);
        sign = Mathf.Sign(cross.y);

        if (distance < Mathf.Epsilon) sign = 0;

        return distance * sign;
    }
}