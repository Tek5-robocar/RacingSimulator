using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class ViewDropDown : MonoBehaviour
{
    public List<Camera> cameras = new List<Camera>();
                                   
    private TMP_Dropdown dropdown;
    private RawImage selectedCamera;
    void Start()
    {
        dropdown = GetComponent<TMP_Dropdown>();
        dropdown.options.Clear();
        foreach (Camera myCamera in cameras)
        {
            dropdown.options.Add(new TMP_Dropdown.OptionData(myCamera.name));
            myCamera.enabled = false;
        }
        cameras[0].enabled = true;
        dropdown.onValueChanged.AddListener(delegate
        {
            DropdownValueChanged();
        });
    }

    void DropdownValueChanged()
    {
        foreach (Camera myCamera in cameras)
        {
            myCamera.enabled = false;
        }
        cameras[dropdown.value].enabled = true;
    }

    public void AddCamera(Camera myCamera, int carIndex)
    {
        Debug.Log($"Camera {myCamera.name} display to {myCamera.targetDisplay}");
        if (myCamera.name != "Back Camera") return;
        dropdown.options.Add(new TMP_Dropdown.OptionData($"Agent {carIndex}"));
        myCamera.enabled = false;
        cameras.Add(myCamera);
    }

    public void RemoveCamera(Camera myCamera, int carIndex)
    {
        dropdown.value = 0;
        DropdownValueChanged();
        int cameraIndex = dropdown.options.FindIndex(data => data.text == $"Agent {carIndex}");
        Debug.Log($"Camera {myCamera.name} index {cameraIndex}");
        if (cameraIndex < 0) return;
        dropdown.options.RemoveAt(cameraIndex);
        cameras.RemoveAt(cameraIndex);
    }
}
