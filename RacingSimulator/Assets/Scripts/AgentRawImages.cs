using UnityEngine;
using UnityEngine.UI;

public class AgentRawImages : MonoBehaviour
{
    public GameObject agents;
    public ViewDropDown viewDropDown;
    
    void Start()
    {
        Init();
    }

    private void Init()
    {
        for (int i = 0; i < agents.transform.childCount; i++)
        {
            Debug.Log(agents.transform.GetChild(i).name);
            for (int j = 0; j < agents.transform.GetChild(i).childCount; j++)
            {
                foreach (Camera agentCamera in agents.transform.GetChild(i).GetChild(j).GetComponents<Camera>())
                {
                    AddCarView(agentCamera);
                }
            }
        }
    }

    void AddCarView(Camera agentCamera)
    {
        Debug.Log(agentCamera.name);
        // GameObject rawImageGo = new GameObject
        // {
        //     name = agentCamera.name,
        // };
        // rawImageGo.transform.SetParent(this.transform);
        // rawImageGo.transform.localPosition = Vector3.zero;
        // rawImageGo.transform.localScale = Vector3.one;
        // rawImageGo.transform.SetAsFirstSibling();
        // RawImage rawImage = rawImageGo.AddComponent<RawImage>();
        // RenderTexture renderTexture = new RenderTexture(694, 512, 1);
        // agentCamera.targetTexture = renderTexture;
        // RectTransform rawImageRect = rawImage.GetComponent<RectTransform>();
        // rawImageRect.sizeDelta = new Vector2(agentCamera.targetTexture.width, agentCamera.targetTexture.height);
        // rawImage.texture = agentCamera.targetTexture;
        viewDropDown.AddCamera(agentCamera, 0);
    }
}
