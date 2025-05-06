using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class DecorButton : MonoBehaviour
{
    public List<GameObject> decorsToDeactivate;
    public Button button;
    public TextMeshProUGUI buttonText;

    private bool _isActivated = true;

    private void Start()
    {
        buttonText.text = "Disable Decor";
        button.onClick.AddListener(OnClick);
    }

    private void OnClick()
    {
        if (_isActivated)
        {
            buttonText.text = "Enable Decor";
            foreach (var decorElem in decorsToDeactivate) decorElem.SetActive(false);
        }
        else
        {
            buttonText.text = "Disable Decor";
            foreach (var decorElem in decorsToDeactivate) decorElem.SetActive(true);
        }

        _isActivated = !_isActivated;
    }
}