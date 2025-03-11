using System.Collections.Generic;
using UnityEngine;

public class RenderTextureToString : MonoBehaviour
{
    private static Texture2D _texture2D;

    public static List<int> ConvertRenderTextureToFile(RenderTexture renderTexture, int numberRay, float fieldView = 100f)
    {
        var currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;

        if (_texture2D == null)
            _texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        _texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        _texture2D.Apply();

        RenderTexture.active = currentRT;

        var angleOffset = fieldView / (numberRay - 1);
        var stepSize = 1;

        var distances = new List<int>();
        for (var k = 0; k < numberRay; k++)
        {
            var hit = false;
            float x = _texture2D.width / 2f;
            float y = _texture2D.height - 1f;
            var hitDist = 0;

            while (x >= 0 && x < _texture2D.width && y >= 0 && y < _texture2D.height)
            {
                var angle = k * angleOffset * Mathf.PI / 180 +
                            angleOffset * Mathf.PI / 180 * ((180 - fieldView) / angleOffset / 2);
                var roundedX = Mathf.FloorToInt(x);
                var roundedY = Mathf.FloorToInt(y);
                var pixelColor = _texture2D.GetPixel(roundedX, _texture2D.height - 1 - roundedY);
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