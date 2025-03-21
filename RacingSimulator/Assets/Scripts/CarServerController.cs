using System;
using System.Collections.Generic;
using System.Net.Sockets;
using TMPro;
using UnityEngine;
using Random = UnityEngine.Random;

public class CarServerController : MonoBehaviour
{
    public CarController carController;
    public Camera carVisionCamera;
    public GameObject canvas;
    public Transform startPosition;
    public TrackDropDown trackDropDown;
    
    private readonly Dictionary<string, Func<float, string>> _floatActions;
    private readonly Dictionary<string, Func<string>> _voidActions;
    private float _fov = 180;
    private bool _isRunning;
    private int _numberRay = 10;
    private RenderTexture _renderTexture;
    private TcpListener _server;
    private TextMeshProUGUI _textMesh;
    private GameObject _textMeshGo;
    private float _timer;
    private readonly List<string> _touchedCheckpoints = new();

    public CarServerController()
    {
        _floatActions = new Dictionary<string, Func<float, string>>
        {
            {
                "SET_SPEED", speed =>
                {
                    if (speed > 1 || speed < -1) return "KO:SET_SPEED";
                    carController?.Move(speed);
                    return "OK:SET_SPEED";
                }
            },
            {
                "SET_STEERING", steering =>
                {
                    if (steering > 1 || steering < -1) return "KO:SET_STEERING";
                    carController?.Turn(steering);
                    return "OK:SET_STEERING";
                }
            },
            {
                "SET_NUMBER_RAY", numberRay =>
                {
                    if (numberRay < 1 || numberRay > 50) return "KO:SET_NUMBER_RAY";
                    this._numberRay = (int)numberRay;
                    return "OK:SET_NUMBER_RAY";
                }
            },
            {
                "SET_FOV", fov =>
                {
                    if (fov < 1 || fov > 180) return "KO:SET_FOV";
                    this._fov = fov;
                    return "OK:SET_FOV";
                }
            }
        };

        _voidActions = new Dictionary<string, Func<string>>
        {
            {
                "GET_SPEED", () =>
                {
                    float? speed = carController?.Speed();
                    if (!speed.HasValue) return "KO:GET_SPEED";

                    return "OK:GET_SPEED:" + speed.Value.ToString("0.00");
                }
            },
            {
                "GET_STEERING", () =>
                {
                    float? steering = carController?.Steering();
                    if (!steering.HasValue) return "KO:GET_STEERING";

                    return "OK:GET_STEERING:" + steering.Value.ToString("0.00");
                }
            },
            {
                "GET_INFOS_RAYCAST", () =>
                {
                    // (List<int> distance, _) = RenderTextureToString.GetRaycasts(carVisionCamera.targetTexture, _numberRay, _fov);
                    // if (distance.Count == _numberRay)
                    // {
                        // string buffer = "OK:GET_INFOS_RAYCAST";
                        // foreach (int distanceToLine in distance)
                        // {
                            // buffer += ":";
                            // buffer += distanceToLine.ToString("0.00");
                        // }

                        // return buffer;
                    // }

                    return "KO:GET_INFOS_RAYCAST";
                }
            },
            {
                "END_SIMULATION", () =>
                {
                    Application.Quit();
                    return "OK:END_SIMULATION";
                }
            },
            {
                "GET_POSITION", () =>
                {
                    Vector3 position = transform.position;
                    return $"OK:GET_POSITION:{position.x:0.00}:{position.y:0.00}:{position.z:0.00}";
                }
            }
            // { "SET_RANDOM_POSITION", () =>
            // {
            //     ResetCarPosition();
            //     Vector3 position = transform.position;
            //     return $"OK:SET_RANDOM_POSITION:{position.x:0.00}:{position.y:0.00}:{position.z:0.00}";
            // } },
        };
    }

    public int NumberCollider { get; set; }

    public int CarIndex { get; set; }

    private void Start()
    {
        _renderTexture = new RenderTexture(694 / 2, 512 / 2, 1);
        carVisionCamera.targetTexture = _renderTexture;

        Random.InitState(DateTime.Now.Millisecond);

        _textMeshGo = new GameObject();
        _textMeshGo.transform.SetParent(canvas.transform);
        _textMeshGo.transform.localPosition = new Vector3(247, 230 - 30 * CarIndex, 0);
        _textMesh = _textMeshGo.AddComponent<TextMeshProUGUI>();
        _textMesh.enableAutoSizing = true;
        _textMesh.color = Color.black;
    }

    private void Update()
    {
        UpdateTimer();
        // carController.Move(Input.GetAxis("Vertical"));
        // carController.Turn(Input.GetAxis("Horizontal"));
    }

    private void FixedUpdate()
    {
        if (transform.position.y < -20) ResetCarPosition();
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Lines"))
        {
            ResetCarPosition();
        }
        else if (other.CompareTag("Checkpoint"))
        {
            if (!_touchedCheckpoints.Contains(other.name)) _touchedCheckpoints.Add(other.name);
        }
        else if (other.CompareTag("Finish"))
        {
            if (_touchedCheckpoints.Count == NumberCollider)
            {
                _timer += Time.deltaTime;
                int minutes = Mathf.FloorToInt(_timer / 60);
                int seconds = Mathf.FloorToInt(_timer % 60);
                Debug.Log($"you finished a lap in {minutes:00}:{seconds:00} !!");
                trackDropDown.UpdateBestScore(_timer);
                _timer = 0f;
            }
            else
            {
                // Debug.Log($"you cheated !! {NumberCollider - _touchedCheckpoints.Count} missing checkpoints");
            }
            _touchedCheckpoints.Clear();
        }
    }


    ~CarServerController()
    {
        Destroy(_textMeshGo);
        Destroy(_textMesh);
    }

    public string HandleClientCommand(string message)
    {
        string stringResponse = "";
        string[] commands = message.Split(';', StringSplitOptions.RemoveEmptyEntries);
        for (int i = 0; i < commands.Length; i++)
        {
            string[] splittedMessage = commands[i].Split(":", StringSplitOptions.RemoveEmptyEntries);
            if (i > 0)
                stringResponse += ";";
            if (splittedMessage.Length == 1)
            {
                if (_voidActions.ContainsKey(splittedMessage[0]))
                    stringResponse += _voidActions[splittedMessage[0]]();
                else
                    stringResponse += $"KO:Unknown command {splittedMessage[0]}";
            }
            else if (splittedMessage.Length == 2)
            {
                if (_floatActions.ContainsKey(splittedMessage[0]))
                    stringResponse += _floatActions[splittedMessage[0]](float.Parse(splittedMessage[1]));
                else
                    stringResponse += $"KO:Unknown command {splittedMessage[0]}";
            }
            else if (splittedMessage.Length > 2)
            {
                stringResponse += $"KO:Command format not supported, lenght is {splittedMessage.Length}";
            }
        }

        return stringResponse;
    }

    public void ResetCarPosition()
    {
        carController.Reset();
        gameObject.transform.position = startPosition.position;
        gameObject.transform.rotation = startPosition.rotation;
        transform.Rotate(new Vector3(0, -90, 0));
        _touchedCheckpoints.Clear();
        _timer = 0f; 
    }

    private void UpdateTimer()
    {
        _timer += Time.deltaTime;
        _textMesh.text = string.Format($"Agent {CarIndex}: {_timer:00}");
    }
}