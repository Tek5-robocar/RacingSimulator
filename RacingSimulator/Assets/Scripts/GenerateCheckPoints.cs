using System;
using UnityEngine;

public class GenerateCheckPoints : MonoBehaviour
{
    public int nbCheckpoint;
    public LineRenderer outsideLineRenderer;
    public Transform agentTransform;
    public GameObject checkpointPrefab;
    public float checkpointLenght;

    private int _id;
    private Vector3[] _lineRendererPoints;

    void Start()
    {
        if (nbCheckpoint <= 0)
            return;
        
        _lineRendererPoints = new Vector3[outsideLineRenderer.positionCount];

        for (int i = 0; i < outsideLineRenderer.positionCount; i++)
        {
            _lineRendererPoints[i] = transform.TransformPoint(outsideLineRenderer.GetPosition(i));
        }

        int lenght = _lineRendererPoints.Length;
        Vector3[] tempPart = new Vector3[lenght];
        int startIndex = GetCloserDistanceIndex(_lineRendererPoints, agentTransform.position);
        
        Array.Copy(_lineRendererPoints, startIndex, tempPart, 0, lenght - startIndex);
        Array.Copy(_lineRendererPoints, 0, _lineRendererPoints, lenght - startIndex, startIndex);
        Array.Copy(tempPart, 0, _lineRendererPoints, 0, lenght - startIndex);

        _id = 0;

        float outsideLineLenghtDivided = LineLenghtSum(_lineRendererPoints) / nbCheckpoint;

        for (int i = 0; i < nbCheckpoint; i++)
        {
            Vector3 startPoint = agentTransform.position;
            
            (Vector3, Vector3, float) outsideLineSurroundings =
                GetSurroundingPoint(_lineRendererPoints, outsideLineLenghtDivided * (i + 1));
            Vector3 outsideCheckpoint = GetPointInBetween(outsideLineSurroundings.Item1, outsideLineSurroundings.Item2,
                outsideLineSurroundings.Item3);

            Vector3 oppositePoint = GetOppositePoint(outsideLineSurroundings.Item1, outsideLineSurroundings.Item2,
                outsideCheckpoint, checkpointLenght);
            AddCheckPoint(outsideCheckpoint, oppositePoint);
        }
    }


    private int GetCloserDistanceIndex(Vector3[] line, Vector3 point)
    {
        float closerDistance = -1;
        int closerDistanceIndex = -1;

        for (int i = 0; i < line.Length; i++)
        {
            float distance = Vector3.Distance(line[i], point);

            if (distance < closerDistance || Mathf.Approximately(closerDistanceIndex, -1))
            {
                closerDistance = distance;
                closerDistanceIndex = i;
            }
        }
        return closerDistanceIndex;
    }


    private Vector3 GetOppositePoint(Vector3 p1, Vector3 p2, Vector3 p3, float distance)
    {
        float x = p3.x + distance * (-(p2.z - p1.z) / Vector3.Distance(p1, p2));
        float z = p3.z + distance * ((p2.x - p1.x) / Vector3.Distance(p1, p2));
        return new Vector3(x, 0, z);
    }

    private Vector3 GetPointInBetween(Vector3 u, Vector3 v, float d)
    {
        float t = d / Vector3.Distance(u, v);
        return new Vector3(u.x + t * (v.x - u.x), u.y + t * (v.y - u.y), u.z + t * (v.z - u.z));
    }

    private (Vector3, Vector3, float) GetSurroundingPoint(Vector3[] line, float distance)
    {
        for (int i = 0; i < line.Length - 1; i++)
        {
            Vector3 p1 = line[i];
            Vector3 p2 = line[i + 1];
            float lenght = Vector3.Distance(p1, p2);

            if (distance < lenght)
            {
                return (p1, p2, distance);
            }

            distance -= lenght;
        }

        return (line[^2], line[^1], 0);
    }

    private float LineLenghtSum(Vector3[] line)
    {
        float sum = 0f;

        for (int i = 0; i < line.Length - 1; i++)
        {
            sum += Vector3.Distance(line[i], line[i + 1]);
        }

        return sum;
    }
    
    private void AddCheckPoint(Vector3 vect1, Vector3 vect2, bool final = false)
    {
        GameObject newGameObject = Instantiate(checkpointPrefab);
        newGameObject.name = final ? "0" : _id.ToString();
        _id++;

        newGameObject.transform.position = (vect1 + vect2) / 2;
        float size = Vector3.Distance(vect1, vect2);
        newGameObject.transform.localScale = new Vector3(size, 1f, 1f);
        Vector3 direction = (vect2 - vect1).normalized;
        newGameObject.transform.rotation = Quaternion.FromToRotation(Vector3.right, direction);
    }
}