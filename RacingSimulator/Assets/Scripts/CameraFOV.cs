using UnityEngine;

public class CameraFOVCalculator : MonoBehaviour
{
    public float diagonalFOV = 81f;
    public float horizontalFOV = 69f;

    public RenderTexture targetTexture;

    private void Start()
    {
        var dfovRad = Mathf.Deg2Rad * diagonalFOV;
        var hfovRad = Mathf.Deg2Rad * horizontalFOV;

        var aspectRatio = Mathf.Tan(hfovRad / 2) / Mathf.Sqrt(Mathf.Tan(dfovRad / 2) * Mathf.Tan(dfovRad / 2) -
                                                              Mathf.Tan(hfovRad / 2) * Mathf.Tan(hfovRad / 2));

        var vfovRad = 2 * Mathf.Atan(Mathf.Tan(hfovRad / 2) / aspectRatio);
        var verticalFOV = vfovRad * Mathf.Rad2Deg;

        var cam = GetComponent<Camera>();
        cam.fieldOfView = verticalFOV;
        cam.aspect = aspectRatio;

        if (targetTexture != null)
        {
            float textureWidth = targetTexture.width;
            float textureHeight = targetTexture.height;

            targetTexture.width = Mathf.RoundToInt(textureHeight * aspectRatio);

            Debug.Log("Render Texture resized to: " + targetTexture.width + "x" + targetTexture.height);
        }

        // Debug.Log("Calculated Aspect Ratio: " + aspectRatio);
        // Debug.Log("Calculated VFOV: " + verticalFOV);
    }
}