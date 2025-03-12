using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class TrackDropDown : MonoBehaviour
{
    public List<GameObject> tracks = new List<GameObject>();
    public GameObject agents;
    public LapManager lapManager;
                                   
    private TMP_Dropdown dropdown;
    private GameObject selectedTrack;
    void Start()
    {
        dropdown = GetComponent<TMP_Dropdown>();
        dropdown.options.Clear();
        foreach (GameObject track in tracks)
        {
            dropdown.options.Add(new TMP_Dropdown.OptionData(track.name));
            track.SetActive(false);
        }

        tracks[0].SetActive(true);
        lapManager.SetTrack(tracks[0]);
        dropdown.onValueChanged.AddListener(delegate
        {
            DropdownValueChanged();    
        });
    }

    void DropdownValueChanged()
    {
        foreach (GameObject track in tracks)
        {
            track.SetActive(false);
        }
        tracks[dropdown.value].SetActive(true);
        lapManager.SetTrack(tracks[dropdown.value]);
        for (int i = 0; i < agents.transform.childCount; i++)
        {
            CarServerController carServerController = agents.transform.GetChild(i).GetComponent<CarServerController>();
            if (carServerController != null)
            {
                carServerController.ResetCarPosition();
            }
        }
    }
}