using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class ViewDropDown : MonoBehaviour
{
    public List<Camera> cameras = new();

    private TMP_Dropdown _dropdown;
    private RawImage _selectedCamera;

    private void Start()
    {
        _dropdown = GetComponent<TMP_Dropdown>();
        _dropdown.options.Clear();
        foreach (var myCamera in cameras)
        {
            _dropdown.options.Add(new TMP_Dropdown.OptionData(myCamera.name));
            myCamera.enabled = false;
        }

        cameras[0].enabled = true;
        _dropdown.onValueChanged.AddListener(delegate { DropdownValueChanged(); });
    }

    private void DropdownValueChanged()
    {
        foreach (var myCamera in cameras) myCamera.enabled = false;
        cameras[_dropdown.value].enabled = true;
    }

    public void AddCamera(Camera myCamera, int carIndex)
    {
        if (myCamera == null) return;
        if (myCamera.name != "Back Camera") return;
        _dropdown.options.Add(new TMP_Dropdown.OptionData($"Agent {carIndex}"));
        myCamera.enabled = false;
        cameras.Add(myCamera);
    }

    public void RemoveCamera(Camera myCamera, int carIndex)
    {
        _dropdown.value = 0;
        DropdownValueChanged();
        var cameraIndex = _dropdown.options.FindIndex(data => data.text == $"Agent {carIndex}");
        if (cameraIndex < 0) return;
        _dropdown.options.RemoveAt(cameraIndex);
        cameras.RemoveAt(cameraIndex);
    }
}