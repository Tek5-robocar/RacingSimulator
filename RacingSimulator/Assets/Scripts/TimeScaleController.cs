using UnityEngine;

public class TimeScaleController : MonoBehaviour
{
    [Range(1f, 20f)] public float timeScale = 1f;
    
    void Start()
    {
        Time.timeScale = timeScale;
    }
}