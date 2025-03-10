using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target; // The car (target to follow)
    public float distance = 5.0f; // Distance behind the car
    public float height = 2.0f; // Height above the car

    private void LateUpdate()
    {
        // Calculate the desired position directly behind the car
        var desiredPosition = target.position - target.forward * distance + Vector3.up * height;

        // Set the camera's position
        transform.position = desiredPosition;

        // Ensure the camera is always looking at the car
        transform.LookAt(target.position +
                         Vector3.up * 1.0f); // Adjust the 1.0f to make the camera look slightly above the car
    }
}