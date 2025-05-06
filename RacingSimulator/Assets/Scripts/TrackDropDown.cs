using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class TrackDropDown : MonoBehaviour
{
    public List<GameObject> tracks = new();
    public GameObject agents;
    public CentralLine lapManager;
    public TextMeshProUGUI bestScoreText;

    private TMP_Dropdown _dropdown;
    private GameObject _selectedTrack;
    private List<(string, float)> _tracksBest;

    private void Start()
    {
        _dropdown = GetComponent<TMP_Dropdown>();
        _dropdown.options.Clear();
        foreach (var track in tracks)
        {
            _dropdown.options.Add(new TMP_Dropdown.OptionData(track.name));
            track.SetActive(false);
        }

        tracks[0].SetActive(true);
        lapManager.SetTrack(tracks[0]);
        _dropdown.onValueChanged.AddListener(delegate { DropdownValueChanged(); });

        _tracksBest = BinarySaveManager.LoadTracks();
        UpdateBestScore();
    }

    public void UpdateBestScore(float bestScore = -1)
    {
        var activeTrack = tracks[_dropdown.value].name;

        Debug.Log($"new score of {bestScore} for {activeTrack}");
        var trackBestExist = false;
        for (var i = 0; i < _tracksBest.Count; i++)
            if (_tracksBest[i].Item1 == activeTrack)
            {
                trackBestExist = true;
                if ((!Mathf.Approximately(bestScore, -1) && bestScore < _tracksBest[i].Item2) ||
                    Mathf.Approximately(_tracksBest[i].Item2, -1)) _tracksBest[i] = (activeTrack, bestScore);
                var minutes = Mathf.FloorToInt(_tracksBest[i].Item2 / 60);
                var seconds = Mathf.FloorToInt(_tracksBest[i].Item2 % 60);
                bestScoreText.text = $"Best Score: {minutes:00}:{seconds:00}";
            }

        if (!trackBestExist)
        {
            _tracksBest.Add((activeTrack, bestScore));
            var minutes = Mathf.FloorToInt(_tracksBest[^1].Item2 / 60);
            var seconds = Mathf.FloorToInt(_tracksBest[^1].Item2 % 60);
            bestScoreText.text = $"Best Score: {minutes:00}:{seconds:00}";
        }

        BinarySaveManager.SaveTracks(_tracksBest);
    }

    private void DropdownValueChanged()
    {
        for (var i = 0; i < agents.transform.childCount; i++)
        {
            var carServerController = agents.transform.GetChild(i).GetComponent<CarContinuousController>();
            if (carServerController != null)
            {
                carServerController.resetCarPosition = true;
                carServerController.EndEpisode();
            }

            ;
        }

        foreach (var track in tracks) track.SetActive(false);
        tracks[_dropdown.value].SetActive(true);
        lapManager.SetTrack(tracks[_dropdown.value]);
        UpdateBestScore();
    }
}