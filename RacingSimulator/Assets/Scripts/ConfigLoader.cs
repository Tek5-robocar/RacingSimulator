using UnityEngine;
using System.IO;
using System;
using Random = UnityEngine.Random;

public class ConfigLoader : MonoBehaviour
{
    public GameObject agents;
    public GameObject agentPrefab;
    public Transform startPosition;
    public GameObject canvas;
    
    private const string EditorConfigPath = "Assets/agents-config.json";
    private readonly string _materialFolderPath = Path.Combine("CarMaterialVariation");
    private Material[] _materials;
    private ViewDropDown _viewDropDown;
    private TrackDropDown _trackDropDown;
    private CentralLine _centralLine;

    void Start()
    {
        _viewDropDown = canvas.GetComponentInChildren<ViewDropDown>();
        _trackDropDown = canvas.GetComponentInChildren<TrackDropDown>();
        _centralLine = canvas.GetComponentInChildren<CentralLine>();
        if (_viewDropDown == null || _trackDropDown == null || _centralLine == null)
        {
            Debug.LogError("Could not find View or Track drop dropdown or central line in canvas.");
            Application.Quit();
        }
        _materials = Resources.LoadAll<Material>(_materialFolderPath);
        string configPath = GetConfigPath();
        if (!string.IsNullOrEmpty(configPath))
        {
            LoadConfig(configPath);
        }
        else
        {
            Debug.LogError("Config file path is null or empty!");
        }
    }

    string GetConfigPath()
    {
        if (Application.isEditor)
        {
            return EditorConfigPath;
        }
        else
        {
            string[] args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--config-path" && i + 1 < args.Length)
                {
                    return args[i + 1];
                }
            }
            Debug.LogError("No config file path provided! Use --config-path /path/to/config.json");
            return null;
        }
    }

    void LoadConfig(string path)
    {
        try
        {
            string json = File.ReadAllText(path);
            ConfigData config = JsonUtility.FromJson<ConfigData>(json);
            for (int i = 0; i < config.agents.Length; i++)
            {
                Debug.Log($"Initializing agent with FOV={config.agents[i].fov}, NbRay={config.agents[i].nbRay}");
                InitializeAgent(config.agents[i], i);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to load config: {e.Message}");
            Debug.LogError(e.StackTrace);
        }
    }

    void InitializeAgent(AgentConfig agentConfig, int index)
    {
        var newGo = Instantiate(agentPrefab, agents.transform, true);
        newGo.transform.position = startPosition.position;
        if (_materials.Length > 0)
            for (var i = 0; i < newGo.transform.childCount; i++)
                if (newGo.transform.GetChild(i).name == "Body")
                {
                    var randomMaterial = _materials[Random.Range(0, _materials.Length)];
                    var tempMaterials = newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials;
                    tempMaterials[0] = randomMaterial;
                    newGo.transform.GetChild(i).gameObject.GetComponent<MeshRenderer>().materials = tempMaterials;
                }

        var carsController = newGo.GetComponent<CarContinuousController>();
        Debug.Log($"setting car index to {index}, fov to {agentConfig.fov} and nbRay to {agentConfig.nbRay}");
        carsController.CarIndex = index;
        carsController.Fov = agentConfig.fov;
        carsController.NbRay = agentConfig.nbRay;
        carsController.canvas = canvas;
        carsController.startPosition = startPosition;
        carsController.trackDropDown = _trackDropDown;
        for (var i = 0; i < newGo.transform.childCount; i++)
            foreach (var myCamera in newGo.transform.GetChild(i).GetComponents<Camera>())
                _viewDropDown.AddCamera(myCamera, carsController.CarIndex);

        _centralLine.AddCar(newGo);
        Debug.Log($"Agent initialized with FOV={agentConfig.fov}, NbRay={agentConfig.nbRay}");
    }

    [System.Serializable]
    public class ConfigData
    {
        public AgentConfig[] agents;
    }

    [System.Serializable]
    public class AgentConfig
    {
        public float fov;
        public int nbRay;
    }
}