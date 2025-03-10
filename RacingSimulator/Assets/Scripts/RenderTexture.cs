using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Linq;
using System.Text;

public class RenderTextureToString : MonoBehaviour
{
    public static List<int> ConvertRenderTextureToFile(RenderTexture renderTexture, int numberRay)
    {
        // string filePath = "test.txt";
        // Ensure the RenderTexture is readable
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;

        // Create a Texture2D to read the pixels
        Texture2D texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture2D.Apply();

        RenderTexture.active = currentRT;

        StringBuilder[] grid = new StringBuilder[texture2D.height];
        for (int i = 0; i < grid.Length; i++)
        {
            grid[i] = new StringBuilder("");
            for (int j = 0; j < texture2D.width; j++)
               grid[i].Append("o");
        }
        float fieldView = 100f; // Field of view in degrees
        float angleOffset = fieldView / (numberRay - 1);
        int stepSize = 1;

        for (int y = texture2D.height - 1; y >= 0; y--) // Start from top to bottom
        {
            for (int x = 0; x < texture2D.width; x++)
            {
                Color pixelColor = texture2D.GetPixel(x, y);
                // Check if the pixel is white
                if (pixelColor.r > 0.9f && pixelColor.g > 0.9f && pixelColor.b > 0.9f) // White threshold
                {
                    grid[texture2D.height - 1 - y][x] = 'x';
                }
            }
        }

        // Raycasting logic
        List<int> distances = new List<int>();
        for (int k = 0; k < numberRay; k++)
        {
            bool hit = false;
            float x = texture2D.width / 2;
            float y = texture2D.height - 1;
            int hitDist = 0;

            while (x >= 0 && x < texture2D.width && y >= 0 && y < texture2D.height)
            {
                float angle = k * angleOffset * Mathf.PI / 180 + angleOffset * Mathf.PI / 180 * ((180 - fieldView) / angleOffset / 2);
                int roundedX = Mathf.FloorToInt(x);
                int roundedY = Mathf.FloorToInt(y);

                char c = grid[roundedY][roundedX];

                if (c == 'x')
                {
                    distances.Add(hitDist);
                    hit = true;
                    break;
                }

                grid[(int)(y)][(int)x] = k.ToString()[0];
                x += stepSize * Mathf.Cos(angle);
                y -= stepSize * Mathf.Sin(angle);
                hitDist++;
            }

            if (!hit)
            {
                distances.Add(hitDist);
            }
        }
        // using (StreamWriter sw = File.AppendText(filePath))
        // {
        //     foreach (var stringBuilder in grid)
        //     {
        //         sw.WriteLine(stringBuilder);
        //     }
        // }	
        

        Object.Destroy(texture2D);
        return distances;
    }
}
