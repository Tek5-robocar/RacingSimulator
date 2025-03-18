using System.Collections.Generic;
using UnityEngine;

public class RenderTextureToString : MonoBehaviour
{
    private static Texture2D _texture2D;

    public static List<int> GetRaycasts(RenderTexture renderTexture, int numberRay, float fieldView)
    {
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;

        if (_texture2D == null)
            _texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        _texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        _texture2D.Apply();

        RenderTexture.active = currentRT;

        float angleOffset = fieldView / (numberRay - 1);
        int stepSize = 1;

        List<int> distances = new List<int>();
        for (int k = 0; k < numberRay; k++)
        {
            bool hit = false;
            float x = _texture2D.width / 2f;
            float y = _texture2D.height - 1f;
            int hitDist = 0;

            while (x >= 0 && x < _texture2D.width && y >= 0 && y < _texture2D.height)
            {
                float angle = k * angleOffset * Mathf.PI / 180 +
                              angleOffset * Mathf.PI / 180 * ((180 - fieldView) / angleOffset / 2);
                int roundedX = Mathf.FloorToInt(x);
                int roundedY = Mathf.FloorToInt(y);
                Color pixelColor = _texture2D.GetPixel(roundedX, _texture2D.height - 1 - roundedY);
                if (pixelColor.r > 0.9f && pixelColor.g > 0.9f && pixelColor.b > 0.9f)
                {
                    distances.Add(hitDist);
                    hit = true;
                    break;
                }

                x += stepSize * Mathf.Cos(angle);
                y -= stepSize * Mathf.Sin(angle);
                hitDist++;
            }

            if (!hit) distances.Add(hitDist);
        }
        
        return distances;
    }
}