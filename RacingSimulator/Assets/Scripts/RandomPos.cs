using UnityEngine;
using UnityEngine.UIElements;
using Toggle = UnityEngine.UI.Toggle;

public class RandomPos : MonoBehaviour
{
    public Toggle toggle;
    public TextField textField;
    
    private bool isEnabled = false;
    private float _timer = 0;
    void Start()
    {
        toggle.onValueChanged.AddListener(OnValueChanged);
    }

    private void OnValueChanged(bool value)
    {
        isEnabled = value;
        textField.SetEnabled(isEnabled);
        if (isEnabled)
        {
            _timer = 0;
        }
    }

    private void Update()
    {
        _timer += Time.deltaTime;
    }
}
