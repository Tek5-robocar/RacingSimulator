using System;
using System.Collections.Generic;
using UnityEngine;

public class LapManager : MonoBehaviour
{
    // could handle timers
    public Transform start;
    public Transform end;
    
    private List<GameObject> cars = new List<GameObject>();
    private GameObject track;
    private List<BoxCollider> trackPartsCheckpoints = new List<BoxCollider>();
    private LineRenderer centralLine;
    // private List<(BoxCollider, bool)> checkpoints = new List<(BoxCollider, bool)>();
    private int numberCollider = 0;
    
    void Start()
    {
        
    }

    public void AddCar(GameObject car)
    {
        cars.Add(car);
        CarServerController carController = car.GetComponent<CarServerController>();
        carController.SetNumberCollider(numberCollider);
    }
    
    private int GetClosestVectorIndex(Vector3 target, Vector3[] vectors)
    {
        if (vectors == null || vectors.Length == 0)
        {
            Debug.LogError("The vector array is null or empty.");
            return -1;
        }

        int closestIndex = 0;
        float closestDistance = Vector3.Distance(target, vectors[0]);

        for (int i = 1; i < vectors.Length; i++)
        {
            float distance = Vector3.Distance(target, vectors[i]);
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
        Vector3 direction = point - pivot;
        direction = rotation * direction;
        return pivot + direction;
    }
    private void GenerateCentralLineRendererPart(GameObject part)
    {
        LineRenderer[] lines =  part.GetComponentsInChildren<LineRenderer>();
        if (lines.Length != 2)
        {
            return;
        }
        List<(Vector3, Vector3)> associatedPoints = new List<(Vector3, Vector3)>();
        Vector3[] bigger = new Vector3[lines[0].positionCount > lines[1].positionCount ?  lines[0].positionCount : lines[1].positionCount];
        Vector3[] smaller = new Vector3[lines[0].positionCount > lines[1].positionCount ?  lines[1].positionCount : lines[0].positionCount];

        if (lines[0].positionCount > lines[1].positionCount)
        {
            lines[0].GetPositions(bigger);
            for (int i = 0; i < bigger.Length; i++)
            {
                bigger[i] += lines[0].transform.position;
                bigger[i] = RotatePointAroundPivot(bigger[i], lines[0].transform.position,  lines[0].transform.rotation);
            }
            lines[1].GetPositions(smaller);
            for (int i = 0; i < smaller.Length; i++)
            {
                smaller[i] += lines[1].transform.position;
                smaller[i] = RotatePointAroundPivot(smaller[i], lines[1].transform.position,  lines[1].transform.rotation);
            }
        }
        else
        {
            lines[0].GetPositions(smaller);
            for (int i = 0; i < smaller.Length; i++)
            {
                smaller[i] += lines[0].transform.position;
                smaller[i] = RotatePointAroundPivot(smaller[i], lines[0].transform.position,  lines[0].transform.rotation);
            }
            lines[1].GetPositions(bigger);
            for (int i = 0; i < bigger.Length; i++)
            {
                bigger[i] += lines[1].transform.position;
                bigger[i] = RotatePointAroundPivot(bigger[i], lines[1].transform.position,  lines[1].transform.rotation);
            }
        }
        
        foreach (Vector3 biggerPos in bigger)
        {
            int closestIndex = GetClosestVectorIndex(biggerPos, smaller);
            associatedPoints.Add((biggerPos, smaller[closestIndex]));
        }

        centralLine = part.AddComponent<LineRenderer>();
        centralLine.positionCount = associatedPoints.Count;

        for (int i = 0; i < associatedPoints.Count; i++)
        {
            Vector3 centralPoint = new Vector3(
                (associatedPoints[i].Item1.x + associatedPoints[i].Item2.x) / 2,
                (associatedPoints[i].Item1.y + associatedPoints[i].Item2.y) / 2,
                (associatedPoints[i].Item1.z + associatedPoints[i].Item2.z) / 2
                );
            centralLine.SetPosition(i, centralPoint);
        }

        var linesColliders = part.AddComponent<LineRendererColliderGenerator>();
        linesColliders.OnStartFinished += () =>
        {
            Debug.Log("start finished");
            foreach (BoxCollider boxCollider in linesColliders.GetColliders())
            {
                numberCollider++;
                // (BoxCollider boxCollider, bool) checkpointStatus = (boxCollider, false);
                // checkpoints.Add(checkpointStatus);
                // checkPoint.tagToCollideWith = "Player";
                boxCollider.name = $"checkpoint_{numberCollider}";
                boxCollider.tag = "Checkpoint";
                // checkPoint.OnCollisionEnter += () =>
                // {
                //     checkpointStatus.Item2 = true;
                //     Debug.Log("collision !!");
                // };
            }
            // Debug.Log($"finished, length: {checkpoints.Count}");
            // foreach (GameObject car in cars)
            // {
                // CarServerController carController = car.GetComponent<CarServerController>();
                // carController.SetCheckPoints(checkpoints);
            // }
        };
    }

    private void GenerateCentralLineRenderer()
    {
        for (int i = 0; i < track.transform.childCount; i++)
        {
            Debug.Log(track.transform.GetChild(i).name);
            GenerateCentralLineRendererPart(track.transform.GetChild(i).gameObject);
        }
    }

    public void SetTrack(GameObject track)
    {
        this.track =  track;
        GenerateCentralLineRenderer();
        // trackPartsCheckpoints.Clear();
        // for (int i = 0; i < track.transform.childCount; i++)
        // {
            // Debug.Log(track.transform.GetChild(i).name);
            // List<LineRenderer> lineRenderers = new List<LineRenderer>();
            // for (int j = 0; j < track.transform.GetChild(i).transform.childCount; j++)
            // {
            //     if (track.transform.GetChild(i).transform.GetChild(j).CompareTag("Lines"))
            //     {
            //         lineRenderers.Add(track.transform.GetChild(i).transform.GetChild(j).gameObject.GetComponent<LineRenderer>());
            //     }
            // }
            //
            // Debug.Log(lineRenderers.Count);
            // if (lineRenderers.Count == 1)
            // {
            //     // lineRenderers.Add(lineRenderers[0]);
            // }
            //
            // if (lineRenderers.Count != 2)
            // {
            //     continue;
            // }
            //
            // BoxCollider newCollider = track.transform.GetChild(i).AddComponent<BoxCollider>();
            // newCollider.isTrigger = true;
            // newCollider.center = new Vector3(
            //     (lineRenderers[0].transform.position.x + lineRenderers[1].transform.position.x) / 2,
            //     (lineRenderers[0].transform.position.y + lineRenderers[1].transform.position.y) / 2,
            //     (lineRenderers[0].transform.position.z + lineRenderers[1].transform.position.z) / 2
            //     );
            // newCollider.size = Vector3.one * 50;
            // trackPartsCheckpoints.Add(newCollider);
            // Debug.Log("checkpoint added");
        // }
    }

    public void RemoveCar(GameObject car)
    {
        cars.Remove(car);
    }

    

    void Update()
    {
        
    }
}
