using UnityEngine;

public class CameraFOVCalculator : MonoBehaviour
{
    public float diagonalFOV = 81f; // DFOV in degrees
    public float horizontalFOV = 69f; // HFOV in degrees

    public RenderTexture targetTexture; // The render texture that the camera renders to

    void Start()
    {
        // Convert input fields to radians
        float dfovRad = Mathf.Deg2Rad * diagonalFOV;
        float hfovRad = Mathf.Deg2Rad * horizontalFOV;

        // Calculate the aspect ratio from DFOV and HFOV
        float aspectRatio = Mathf.Tan(hfovRad / 2) / Mathf.Sqrt(Mathf.Tan(dfovRad / 2) * Mathf.Tan(dfovRad / 2) - Mathf.Tan(hfovRad / 2) * Mathf.Tan(hfovRad / 2));

        // Calculate VFOV
        float vfovRad = 2 * Mathf.Atan(Mathf.Tan(hfovRad / 2) / aspectRatio);
        float verticalFOV = vfovRad * Mathf.Rad2Deg;

        // Set Unity camera's VFOV and aspect ratio
        Camera cam = this.GetComponent<Camera>();
        cam.fieldOfView = verticalFOV;
        cam.aspect = aspectRatio;

        // Adjust the RenderTexture's aspect ratio by changing its width and height
        if (targetTexture != null)
        {
            // Resize the render texture based on the aspect ratio of the camera
            float textureWidth = targetTexture.width;
            float textureHeight = targetTexture.height;

            // Adjust the render texture width to match the camera's aspect ratio
            targetTexture.width = Mathf.RoundToInt(textureHeight * aspectRatio);

            // Optionally log the changes for debugging
            Debug.Log("Render Texture resized to: " + targetTexture.width + "x" + targetTexture.height);
        }

        // Log aspect ratio and VFOV for debugging
        Debug.Log("Calculated Aspect Ratio: " + aspectRatio);
        Debug.Log("Calculated VFOV: " + verticalFOV);
    }
}