﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class BeeAgent : Agent { 
    private float goalDistance, beeProx;
    Beehive goal;
    Honeycomb targ;
    GameplayManager lifeRankScore;
    GestureManager aiNav;

    [Header("Specific to AgentBeeLow")]
    public GameObject B;

    public override List<float> CollectState()
	{
		List<float> state = new List<float>();

		return state;
	}

	public override void AgentStep(float[] act)
	{

	}
    /*
	public override void AgentReset()
	{

	}
    */
	public override void AgentOnDone()
	{
         
	}

    public override string ToString()
    {
        return base.ToString();
    }

    public override int GetHashCode()
    {
        return base.GetHashCode();
    }

    
    public override void InitializeAgent()
    {
        base.InitializeAgent();
    }
}
