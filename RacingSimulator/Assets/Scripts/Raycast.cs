using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class Raycast : MonoBehaviour
{
    public Button RaycastButton;
    public TextMeshProUGUI RaycastButtonText;

    private bool isEnabled = true;

    private void Start()
    {
        RaycastButton.onClick.AddListener(() =>
        {
            RaycastButtonText.text = isEnabled ? "Enable Raycast" : "Disable Raycast";
            isEnabled = !isEnabled;
        });
    }

    public (List<int>, Texture2D) GetRaycasts(RenderTexture renderTexture, Texture2D texture2D, int numberRay,
        float fieldView)
    {
        // Debug.Log(RenderTexture.active.name);
        var currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;
        // Debug.Log(RenderTexture.active.name);
        if (texture2D == null)
            texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        texture2D.Apply();

        RenderTexture.active = currentRT;

        var angleOffset = fieldView / (numberRay - 1);
        var stepSize = 1;

        var distances = new List<int>();
        for (var k = 0; k < numberRay; k++)
        {
            var hit = false;
            var x = texture2D.width / 2f;
            var y = texture2D.height - 1f;
            var hitDist = 0;

            while (x >= 0 && x < texture2D.width && y >= 0 && y < texture2D.height)
            {
                var angle = k * angleOffset * Mathf.PI / 180 +
                            angleOffset * Mathf.PI / 180 * ((180 - fieldView) / angleOffset / 2);
                var roundedX = Mathf.FloorToInt(x);
                var roundedY = Mathf.FloorToInt(y);
                var pixelColor = texture2D.GetPixel(roundedX, texture2D.height - 1 - roundedY);
                if (pixelColor.r > 0.9f && pixelColor.g > 0.9f && pixelColor.b > 0.9f)
                {
                    distances.Add(hitDist);
                    hit = true;
                    break;
                }

                if (isEnabled)
                    texture2D.SetPixel(roundedX, texture2D.height - 1 - roundedY, Color.blue);

                x += stepSize * Mathf.Cos(angle);
                y -= stepSize * Mathf.Sin(angle);
                hitDist++;
            }

            if (!hit) distances.Add(hitDist);
        }

        texture2D.Apply();

        return (distances, texture2D);
    }
}