﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class BeeDecision : MonoBehaviour, Decision
{

    public float[] Decide(List<float> state, List<Camera> observation, float reward, bool done, float[] memory)
    {
        if (gameObject.GetComponent<Brain>().brainParameters.actionSpaceType == StateType.continuous)
        {
            return new float[4] { 0f, 0f, 0f, 0.0f };

        }
        else
        {
            return new float[1] { 1f };
        }
    }

    public float[] MakeMemory(List<float> state, List<Camera> observation, float reward, bool done, float[] memory)
    {
        try
        {
            float[] v = new float[0];
            return v;
        }
        catch
        {
            return System.Array.Empty<float>();
        }

    }
}
