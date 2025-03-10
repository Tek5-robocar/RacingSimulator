using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.CompilerServices;
using UnityEngine;
using UnityEngine.UI;

public class Mask
{
    public enum CollideRegion
    {
        BottomLeft = 0,
        LeftLine = 1,
        Top = 2,
        RightLine = 3,
        BottomRight = 4,
    }
    
    public static List<(CollideRegion, float)> GetDistancesToLines(float rayDistance, Camera cameraToCapture, LayerMask object1Layer, LayerMask object2Layer, int numberRay, int fieldOfView)
    {
        float width = cameraToCapture.pixelWidth;
        float height = cameraToCapture.pixelHeight;
        
        List<(CollideRegion, float)> hits = new List<(CollideRegion, float)>();
        float angleOffset = fieldOfView / (numberRay - 1f);
        float stepSize = 1f;
        for (int k = 0; k < numberRay; k++)
        {
            double x = width / 2f; // Row index
            double y = 0; // Column index
            int hitDistance = 0;
            while (x >= 0 && x < width && y >= 0 && y < height)
            {
                double angle = k * angleOffset * Math.PI / 180.0 + angleOffset * Math.PI / 180 * ((180 - fieldOfView) / angleOffset / 2);
                int roundedX = (int)Math.Floor(x);
                int roundedY = (int)Math.Floor(y);
                float normalizedX = (float)roundedX / (float)(width - 1);
                float normalizedY = (float)roundedY / (float)(height - 1);
                Ray ray = cameraToCapture.ViewportPointToRay(new Vector3(normalizedX, normalizedY, 0));
                if (Physics.Raycast(ray, out RaycastHit hit, rayDistance))
                {
                    if ((object1Layer.value & (1 << hit.collider.gameObject.layer)) > 0)
                    {
                        hits.Add((CollideRegion.LeftLine, hitDistance));
                        break;
                    }
                    if ((object2Layer.value & (1 << hit.collider.gameObject.layer)) > 0)
                    {
                        hits.Add((CollideRegion.RightLine, hitDistance));
                        break;
                    }
                }
                x += stepSize * Math.Cos(angle); // Move in the X direction (row)
                y += stepSize * Math.Sin(angle); // Move in the Y direction (column)
                hitDistance++;
            }

            if (hits.Count <= k)
            {
                if (hits.Count > 0 && hits[^1].Item1 == CollideRegion.RightLine)
                {
                    hits.Add((CollideRegion.Top, hitDistance));
                } else if (hits.Count > 0 && hits[^1].Item1 == CollideRegion.LeftLine)
                {
                    hits.Add((CollideRegion.BottomLeft, hitDistance));
                }
                else if (hits.Count > 0)
                {
                    hits.Add((hits[^1].Item1, hitDistance));
                }
                else
                {
                    hits.Add((CollideRegion.BottomRight, hitDistance));
                }
            }
        }
        return hits;
    }
    
    static int[,] CreateObjectMatrix(int matrixWidth, int matrixHeight, float rayDistance, Camera cameraToCapture, LayerMask object1Layer, LayerMask object2Layer)
    {
        int[,] objectMatrix = new int[matrixWidth, matrixHeight];
        for (int y = 0; y < matrixHeight; y++)
        {
            for (int x = 0; x < matrixWidth; x++)
            {
                float normalizedX = (float)x / (float)matrixWidth;
                float normalizedY = (float)y / (float)matrixHeight;

                Ray ray = cameraToCapture.ViewportPointToRay(new Vector3(normalizedX, normalizedY, 0));
            
                if (Physics.Raycast(ray, out RaycastHit hit, rayDistance))
                {
                    if ((object1Layer.value & (1 << hit.collider.gameObject.layer)) > 0)
                    {
                        objectMatrix[x, y] = 1;
                    }
                    else if ((object2Layer.value & (1 << hit.collider.gameObject.layer)) > 0)
                    {
                        objectMatrix[x, y] = 2;
                    }
                    else
                    {
                        objectMatrix[x, y] = 0;
                    }
                }
                else
                {
                    objectMatrix[x, y] = 0;
                }
            }
        }
        return objectMatrix;
    }

    static int[,] MirrorMatrixY(int[,] matrix, int matrixWidth, int matrixHeight)
    {
        for (int y = 0; y < matrixHeight / 2; y++)
        {
            for (int x = 0; x < matrixWidth; x++)
            {
                (matrix[x, y], matrix[x, matrixHeight - y - 1]) = (matrix[x, matrixHeight - y - 1], matrix[x, y]);
            }
        }
        return matrix;
    }
    
    public static int[,] GetObjectMatrix(int matrixWidth, int matrixHeight, float rayDistance, Camera cameraToCapture, LayerMask object1Layer, LayerMask object2Layer)
    {
        return MirrorMatrixY(CreateObjectMatrix(matrixWidth, matrixHeight, rayDistance, cameraToCapture, object1Layer, object2Layer), matrixWidth, matrixHeight);
    }

    public static void SaveMask(string saveFilePath, float rayDistance, Camera cameraToCapture, LayerMask object1Layer, LayerMask object2Layer)
    {
        int[,] objectMatrix = CreateObjectMatrix(cameraToCapture.pixelWidth, cameraToCapture.pixelHeight, rayDistance, cameraToCapture, object1Layer, object2Layer);

        Texture2D textureLeft = new Texture2D(cameraToCapture.pixelWidth, cameraToCapture.pixelHeight, TextureFormat.RGBA32, false);
        Texture2D textureRight = new Texture2D(cameraToCapture.pixelWidth, cameraToCapture.pixelHeight, TextureFormat.RGBA32, false);
        for (int y = 0; y < cameraToCapture.pixelHeight; y++)
        {
            for (int x = 0; x < cameraToCapture.pixelWidth; x++)
            {
                switch (objectMatrix[x, y])
                {
                    case 0:
                        textureLeft.SetPixel(x, y, Color.black);
                        textureRight.SetPixel(x, y, Color.black);
                        break;
                    case 2:
                        textureLeft.SetPixel(x, y, Color.white);
                        textureRight.SetPixel(x, y, Color.black);
                        break;
                    case 1:
                        textureLeft.SetPixel(x, y, Color.black);
                        textureRight.SetPixel(x, y, Color.red);
                        break;
                    default:
                        break;
                }
            }
        }

        textureLeft.Apply();
        textureRight.Apply();
        byte[] bytesLeft = textureLeft.EncodeToPNG();
        byte[] bytesRight = textureRight.EncodeToPNG();
        
        string directory = Path.GetDirectoryName(saveFilePath);
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
        
        int lastDelimiter = saveFilePath.LastIndexOf('/');
        File.WriteAllBytes(saveFilePath.Substring(0, lastDelimiter) + saveFilePath.Substring(lastDelimiter).Replace(".png", "") + "-left" + ".png", bytesLeft);
        File.WriteAllBytes(saveFilePath.Substring(0, lastDelimiter) + saveFilePath.Substring(lastDelimiter).Replace(".png", "") + "-right" + ".png", bytesRight);
    }
}
