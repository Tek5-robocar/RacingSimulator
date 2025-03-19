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
    void Start()
    {
        buttonText.text = "Deactivate Decor";
        button.onClick.AddListener(OnClick);
    }

    private void OnClick()
    {
        if (_isActivated)
        {
            buttonText.text = "Activate Decor";
            foreach (GameObject decorElem in decorsToDeactivate)
            {
                decorElem.SetActive(false);
            }
        }
        else
        {
            buttonText.text = "Deactivate Decor";
            foreach (GameObject decorElem in decorsToDeactivate)
            {
                decorElem.SetActive(true);
            }
        }
        _isActivated = !_isActivated;
    }
}
