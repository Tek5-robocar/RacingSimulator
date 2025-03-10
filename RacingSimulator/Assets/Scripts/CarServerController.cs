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
    
    private int numberRay = 10;
    private readonly Dictionary<string, Func<float, string>> floatActions;
    private readonly Dictionary<string, Func<string>> voidActions;
    private TcpListener server;
    private bool isRunning;
    private RenderTexture renderTexture;
    private float timer = 0f;
    private GameObject textMeshGo;
    private TextMeshProUGUI textMesh;

    ~CarServerController()
    {
        Destroy(textMeshGo);
        Destroy(textMesh);
    }
    
    public int CarIndex {get; set;}
    
    public CarServerController()
    {
        floatActions = new Dictionary<string, Func<float, string>>
        {
            { "SET_SPEED", (float speed) =>
            {
                if (speed > 1 || speed < -1)
                {
                    return "KO:SET_SPEED";
                }
                this.carController?.Move(speed);
                return "OK:SET_SPEED";
            } },
            { "SET_STEERING", (float steering) =>
            {
                if (steering > 1 || steering < -1)
                {
                    return "KO:SET_STEERING";
                }
                this.carController?.Turn(steering);
                return "OK:SET_STEERING";
            } },
            { "SET_NUMBER_RAY", (float numberRay) =>
            {
                if (numberRay < 1 || numberRay > 50)
                {
                    return "KO:SET_NUMBER_RAY";
                }
                this.numberRay = (int)numberRay;
                return "OK:SET_STEERING";
            } },
        };
        
        voidActions = new Dictionary<string, Func<string>>
        {
            { "GET_SPEED", () =>
            {
                float? speed = this.carController?.Speed();
                if (!speed.HasValue)
                {
                    return "KO:GET_SPEED";
                }
                else
                {
                    return "OK:GET_SPEED:" + speed.Value.ToString("0.00");
                }
            } },
            { "GET_STEERING", () => {
                float? steering = this.carController?.Steering();
                if (!steering.HasValue)
                {
                    return "KO:GET_STEERING";
                }
                else
                {
                    return "OK:GET_STEERING:" + steering.Value.ToString("0.00");
                }
            } },
            { "GET_INFOS_RAYCAST", () =>
            {
                List<int> distance = RenderTextureToString.ConvertRenderTextureToFile(carVisionCamera.targetTexture, numberRay);
                if (distance.Count == numberRay)
                {
                    string buffer = "OK:GET_INFOS_RAYCAST";
                    foreach (int distanceToLine in distance)
                    {
                        buffer += ":";
                        buffer += distanceToLine.ToString("0.00");
                    }

                    return buffer;
                }
                return "KO:GET_INFOS_RAYCAST";
            } },
            { "END_SIMULATION", () =>
            {
                Application.Quit();
                return "OK:END_SIMULATION";
            } },
            { "GET_POSITION", () =>
            {
                Vector3 position = transform.position;
                return $"OK:GET_POSITION:{position.x:0.00}:{position.y:0.00}:{position.z:0.00}";
            } },
            // { "SET_RANDOM_POSITION", () =>
            // {
            //     ResetCarPosition();
            //     Vector3 position = transform.position;
            //     return $"OK:SET_RANDOM_POSITION:{position.x:0.00}:{position.y:0.00}:{position.z:0.00}";
            // } },
        };
    }

    void Start()
    {
        renderTexture = new RenderTexture(694, 512,1);
        carVisionCamera.targetTexture = renderTexture;

        Random.InitState(System.DateTime.Now.Millisecond);
        
        textMeshGo = new GameObject();
        textMeshGo.transform.SetParent(canvas.transform);
        textMeshGo.transform.localPosition = new Vector3(247, 230 - 30 * CarIndex, 0);
        textMesh = textMeshGo.AddComponent<TextMeshProUGUI>();
        textMesh.enableAutoSizing = true;
        textMesh.color = Color.black;
    }
    
    public string HandleClientCommand(string message)
    {
        string stringResponse = "";
        string[] commands = message.Split(';');
        for (int i = 0; i < commands.Length; i++)
        {
            string[] splittedMessage = commands[i].Split(":", StringSplitOptions.RemoveEmptyEntries);
            if (i > 0)
                stringResponse += ";";
            if (splittedMessage.Length == 1)
            {
                if (this.voidActions.ContainsKey(splittedMessage[0]))
                {
                    stringResponse += this.voidActions[splittedMessage[0]]();
                }
                else
                {
                    stringResponse += $"KO:Unknown command {splittedMessage[0]}";
                }
            } else if (splittedMessage.Length == 2)
            {
                if (this.floatActions.ContainsKey(splittedMessage[0]))
                {
                    stringResponse += this.floatActions[splittedMessage[0]](float.Parse(splittedMessage[1]));
                }
                else
                {
                    stringResponse += $"KO:Unknown command {splittedMessage[0]}";
                }
            }
            else if (splittedMessage.Length > 2)
            {
                stringResponse += $"KO:Command format not supported, lenght is {splittedMessage.Length}";
            }
        }
        
        return stringResponse;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Lines"))
        {
            ResetCarPosition();
        }
    }
    
    public void ResetCarPosition()
    {
        carController.Reset();
        gameObject.transform.position = startPosition.position;
        gameObject.transform.rotation = startPosition.rotation;
        transform.Rotate(new Vector3(0, -90, 0));
        timer = 0f;
    }
    
    private void UpdateTimer()
    {
        timer += Time.deltaTime;
        int minutes = Mathf.FloorToInt(timer / 60);
        int seconds = Mathf.FloorToInt(timer % 60);
        textMesh.text = string.Format($"Agent {CarIndex}: {minutes:00}:{seconds:00}");
    }
    
    private void Update()
    {
        UpdateTimer();
        if (transform.position.y < -20)
        {
            ResetCarPosition();
        }
        // carController.Move(Input.GetAxis("Vertical"));
        // carController.Turn(Input.GetAxis("Horizontal"));
    }
}