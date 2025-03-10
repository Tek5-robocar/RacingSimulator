using UnityEngine;

public class CarController : MonoBehaviour
{
    [Header("Wheel Colliders")]
    public WheelCollider frontLeftWheel;
    public WheelCollider frontRightWheel;
    public WheelCollider rearLeftWheel;
    public WheelCollider rearRightWheel;

    [Header("Wheel Transforms")]
    public Transform frontLeftTransform;
    public Transform frontRightTransform;
    public Transform rearLeftTransform;
    public Transform rearRightTransform;

    [Header("Car Settings")]
    public float motorForce = 1500f;
    public float passiveBrakeForce = 500f;
    public float directionChangeBrakeForce = 3000f;
    public float maxSteerAngle = 30f;
    public float maxSpeed = 50f;
    public float minSpeed = -50f;
    public float forwardFrictionStiffness = 2f;
    public float sidewaysFrictionStiffness = 2f;

    private float currentSteerAngle;
    private float currentBrakeForce;
    private float currentMotorForce;
    // private bool isBraking;

    private Rigidbody carRigidbody;

    private void AdjustWheelGrip(WheelCollider wheel)
    {
        WheelFrictionCurve forwardFriction = wheel.forwardFriction;
        forwardFriction.stiffness = forwardFrictionStiffness;
        wheel.forwardFriction = forwardFriction;

        WheelFrictionCurve sidewaysFriction = wheel.sidewaysFriction;
        sidewaysFriction.stiffness = sidewaysFrictionStiffness;
        wheel.sidewaysFriction = sidewaysFriction;
    }

    private void Start()
    {
        carRigidbody = GetComponent<Rigidbody>();

        AdjustWheelGrip(frontLeftWheel);
        AdjustWheelGrip(frontRightWheel);
        AdjustWheelGrip(rearLeftWheel);
        AdjustWheelGrip(rearRightWheel);
    }

    public void Reset()
    {
        currentSteerAngle = 0f;
        currentBrakeForce = 0f;
        currentMotorForce = 0f;
        // isBraking = false;
        carRigidbody.linearVelocity = Vector3.zero;
        carRigidbody.angularVelocity = Vector3.zero;
        
        frontLeftWheel.steerAngle = currentSteerAngle;
        frontRightWheel.steerAngle = currentSteerAngle;
        
        frontLeftWheel.motorTorque = 0f;
        frontRightWheel.motorTorque = 0f;
        rearLeftWheel.motorTorque = 0f;
        rearRightWheel.motorTorque = 0f;
    }

    private void FixedUpdate()
    {
        LimitSpeed();
        HandleMotor();
        UpdateWheels();
    }

    public void Move(float force)
    {
        currentMotorForce = force * motorForce;
    }

    private void HandleMotor()
    {
        float currentSpeed = carRigidbody.linearVelocity.magnitude * Mathf.Sign(Vector3.Dot(carRigidbody.linearVelocity, transform.forward));
        bool shouldBrake = (currentMotorForce > 0 && currentSpeed < 0) || (currentMotorForce < 0 && currentSpeed > 0);

        if (shouldBrake)
        {
            currentBrakeForce = directionChangeBrakeForce;
            frontLeftWheel.motorTorque = 0f;
            frontRightWheel.motorTorque = 0f;
            rearLeftWheel.motorTorque = 0f;
            rearRightWheel.motorTorque = 0f;
        }
        else if (Mathf.Abs(currentMotorForce) > 0.01f)
        {
            frontLeftWheel.motorTorque = currentMotorForce;
            frontRightWheel.motorTorque = currentMotorForce;
            rearLeftWheel.motorTorque = currentMotorForce;
            rearRightWheel.motorTorque = currentMotorForce;

            currentBrakeForce = 0f;
        }
        else
        {
            currentBrakeForce = passiveBrakeForce;
        }

        ApplyBraking();
    }

    private void ApplyBraking()
    {
        frontLeftWheel.brakeTorque = currentBrakeForce;
        frontRightWheel.brakeTorque = currentBrakeForce;
        rearLeftWheel.brakeTorque = currentBrakeForce;
        rearRightWheel.brakeTorque = currentBrakeForce;
    }

    public void Turn(float direction)
    {
        // float speedFactor = Mathf.Clamp01(carRigidbody.linearVelocity.magnitude / maxSpeed);
        // float dynamicSteerAngle = maxSteerAngle * (1 - speedFactor);

        currentSteerAngle = maxSteerAngle * direction / 2;
        // currentSteerAngle = dynamicSteerAngle * direction;
        frontLeftWheel.steerAngle = currentSteerAngle;
        frontRightWheel.steerAngle = currentSteerAngle;
    }

    private void UpdateWheels()
    {
        UpdateWheelPose(frontLeftWheel, frontLeftTransform);
        UpdateWheelPose(frontRightWheel, frontRightTransform);
        UpdateWheelPose(rearLeftWheel, rearLeftTransform);
        UpdateWheelPose(rearRightWheel, rearRightTransform);
    }

    private void UpdateWheelPose(WheelCollider wheelCollider, Transform wheelTransform)
    {
        wheelCollider.GetWorldPose(out var pos, out var rot);
        wheelTransform.position = pos;
        wheelTransform.rotation = rot;
    }

    public float Speed()
    {
        return carRigidbody.linearVelocity.magnitude;
    }
    
    public float Steering()
    {
        // float speedFactor = Mathf.Clamp01(carRigidbody.linearVelocity.magnitude / maxSpeed);
        // float dynamicSteerAngle = maxSteerAngle * (1 - speedFactor);

        // return currentSteerAngle / dynamicSteerAngle;
        return currentSteerAngle / maxSteerAngle;
    }

    private void LimitSpeed()
    {
        if (Speed() > maxSpeed || Speed() < minSpeed)
        {
            currentMotorForce = 0f;
        }
    }
}