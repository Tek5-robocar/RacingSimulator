using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif


public class TransformSaver : MonoBehaviour
{
    public bool save;
    public List<Texture> textureList;
    [Range(1, 10)] public int nbLoop = 1;
    [Range(0.01f, 10f)] public float timeOffset = 1f;
    [Range(0.01f, 1f)] public float imageSizeScale = 1;
    [Range(0.01f, 5f)] public float imageToMatrixScale = 1f;
    [Range(0, 180)] public int additionalRotationFieldOfVision = 90;
    [Min(0)] public int numberAdditionalRotation = 1;
    [Min(50)] public int visionDepth = 150;
    [Range(0, 50)] public int linesComparisonTolerance = 1;
    [Range(0, 100)] public int maxBlurPercent;
    [Range(0, 100)] public int blurAmountPercent;
    public string version = "";

    private Transform _cameraTransform;
    private readonly string _posFileName = "pos.txt";
    private readonly string _configFileName = "config.txt";
    private readonly string _dirName = "Datasets";
    private List<string> _posLines = new();

    private void Start()
    {
        if (!save) return;

        _cameraTransform = GetComponentInChildren<Camera>().transform;

        try
        {
            InitVersionDirectory();
            InitConfigFile();
        }
        catch (Exception)
        {
            Debug.LogError($"Could not initialize project");
        }


        if (save)
            StartCoroutine(DoActionEveryTimeOffset());
    }

    private void GetLatestVersion()
    {
        var directories = Directory.GetDirectories(_dirName);
        string[] newVersion = { "0", "0", "0" };

        foreach (var directory in directories)
        {
            int[] dirVersion = { 0, 0, 0 };
            var i = 0;
            foreach (var se in directory.Split('\\')[^1].Split('.')) dirVersion[i++] = int.Parse(se);
            if (dirVersion[0] > int.Parse(newVersion[0]))
            {
                newVersion[0] = dirVersion[0].ToString();
                newVersion[1] = dirVersion[1].ToString();
                newVersion[2] = (dirVersion[2] + 1).ToString();
            }
            else if (dirVersion[0] == int.Parse(newVersion[0]) && dirVersion[1] > int.Parse(newVersion[1]))
            {
                newVersion[1] = dirVersion[1].ToString();
                newVersion[2] = (dirVersion[2] + 1).ToString();
            }
            else if (dirVersion[0] == int.Parse(newVersion[0]) && dirVersion[0] == int.Parse(newVersion[1]) &&
                     dirVersion[2] >= int.Parse(newVersion[2]))
            {
                newVersion[2] = (dirVersion[2] + 1).ToString();
            }
        }

        version = string.Join(".", newVersion);
    }
    
    private void InitVersionDirectory()
    {
        if (!Directory.Exists(_dirName))
            Directory.CreateDirectory(_dirName);

        if (version == "")
            GetLatestVersion();
        Debug.Log($"Using version: {version}");
        try
        {
            if (!Directory.Exists(Path.Join(_dirName, version)))
                Directory.CreateDirectory(Path.Join(_dirName, version));
        }
        catch (Exception e)
        {
            Debug.LogError(e.Message);
            throw;
        }
    }


    private void InitConfigFile()
    {
        if (textureList.Count <= 0)
        {
            Debug.LogError("Texture list is empty");
            #if UNITY_EDITOR
            EditorApplication.isPlaying = false;
            #endif
        }

        List<string> lines = new List<string>
        {
            $"version:{version}",
            $"SETTINGS",
            $"loop:{nbLoop}",
            $"imageWidth:{1920 * imageSizeScale}",
            $"imageHeight:{1080 * imageSizeScale}",
            $"imageToMaskScale:{imageToMatrixScale}",
            $"visionDepth:{visionDepth}",
            $"posFilePath:{Path.Join(_dirName, version, _posFileName)}",
            $"cameraHeight:{(int)_cameraTransform.position.y}",
            $"cameraInclination:{(int)_cameraTransform.eulerAngles.x}",
            $"DATA_AUGMENTATION",
            $"texture:{string.Join(';', textureList.Select(texture => texture.name))}",
            $"additionalRotationFieldOfVision:{additionalRotationFieldOfVision}",
            $"numberAdditionalRotation:{numberAdditionalRotation}",
            $"blurAmountPercent:{blurAmountPercent}",
            $"maxBlurPercent:{maxBlurPercent}",
        };

        try
        {
            File.WriteAllLines(Path.Join(_dirName, version, _configFileName), lines);
        }
        catch (Exception e)
        {
            Debug.LogError(e.Message);
            throw;
        }
    }

    private IEnumerator DoActionEveryTimeOffset()
    {
        while (true)
        {
            _posLines.Add((int)_cameraTransform.position.x + ";" +
                          (int)_cameraTransform.position.z + ";" +
                          (int)_cameraTransform.eulerAngles.y + ";" +
                          (int)_cameraTransform.eulerAngles.z
                          );

            yield return new WaitForSeconds(timeOffset);
        }
    }

    private void OnApplicationQuit()
    {
        _posLines = _posLines.Distinct(new ApproximateStringComparer(linesComparisonTolerance)).ToList();
        File.WriteAllText(Path.Join(_dirName, version, _posFileName), string.Join("\n", _posLines));
    }
}