using System.IO;
using UnityEngine;

public class CameraCapture
{
    public static void CaptureImage(string savePath, Camera cameraToCapture, int blurAmountPercent, int maxBlurPercent)
    { 
        RenderTexture renderTexture = new RenderTexture(cameraToCapture.pixelWidth, cameraToCapture.pixelHeight, 24);
        cameraToCapture.targetTexture = renderTexture;

        RenderTexture.active = renderTexture;
        cameraToCapture.Render();

        Texture2D texture = new Texture2D(cameraToCapture.pixelWidth, cameraToCapture.pixelHeight, TextureFormat.RGB24, false);

        texture.ReadPixels(new Rect(0, 0, cameraToCapture.pixelWidth, cameraToCapture.pixelHeight), 0, 0);
        texture.Apply();

        System.Random r = new System.Random();

        if (r.Next(0, 100) <= blurAmountPercent)
        {
            texture = TextureBlurrer.BlurTexture(texture, r.Next(0, maxBlurPercent));
        }
        
        byte[] imageBytes = texture.EncodeToPNG();

        File.WriteAllBytes(savePath, imageBytes);

        cameraToCapture.targetTexture = null;
        RenderTexture.active = null;
    }
}