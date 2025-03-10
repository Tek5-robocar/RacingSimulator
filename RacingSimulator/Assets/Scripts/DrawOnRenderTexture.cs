using UnityEngine;
using UnityEngine.UI;

public class RenderTextureToRawImage : MonoBehaviour
{
    public RenderTexture renderTexture; // The RenderTexture you want to capture
    public RawImage rawImage;           // The RawImage where the Texture2D will be applied

    private Texture2D texture2D;        // Texture2D to hold the captured image

    void Start()
    {
        // Ensure renderTexture and rawImage are assigned in the inspector
        if (renderTexture != null && rawImage != null)
        {
            // Create a new Texture2D with the same dimensions as the RenderTexture
            texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);
        }
        else
        {
            Debug.LogError("RenderTexture or RawImage is not assigned!");
        }
    }

    void Update()
    {
        if (renderTexture != null && rawImage != null && texture2D != null)
        {
            // Check if the size of the RenderTexture has changed
            if (texture2D.width != renderTexture.width || texture2D.height != renderTexture.height)
            {
                // Recreate the Texture2D with the new size
                texture2D.Reinitialize(renderTexture.width, renderTexture.height);
            }

            // Set the active RenderTexture to the one we want to capture
            RenderTexture.active = renderTexture;

            // Read the pixels from the RenderTexture into the Texture2D
            texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);

            // Apply changes to the Texture2D
            texture2D.Apply();

            // Set the Texture2D to the RawImage
            rawImage.texture = texture2D;

            // Optionally, reset the active RenderTexture
            RenderTexture.active = null;
        }
    }

    // Function to draw a pixel at (x, y) with a given color
    public void DrawPixel(int x, int y, Color color)
    {
        if (x >= 0 && x < texture2D.width && y >= 0 && y < texture2D.height)
        {
            texture2D.SetPixel(x, y, color);  // Set the pixel at (x, y) to the specified color
            texture2D.Apply();  // Apply the changes to the Texture2D
        }
        else
        {
            Debug.LogWarning("Coordinates out of bounds: (" + x + ", " + y + ")");
        }
    }
}
