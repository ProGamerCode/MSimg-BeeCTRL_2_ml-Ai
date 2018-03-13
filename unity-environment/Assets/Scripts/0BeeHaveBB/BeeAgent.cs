using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class BeeAgent : Agent {

    Transform bSelf;
    
    private float goalDistance;
    Beehive goal;
    Honeycomb[] targ;
    GameplayManager lifeRankScore;
    GestureManager aiNav;
    int lives, rank, score;
    [Header("Specific to AgentBeeLow")]
    public GameObject B;
    Honeycomb targActive;

    public override List<float> CollectState()
    {
        lives = lifeRankScore.lives;
        score = lifeRankScore.score;
        List<float> state = new List<float>();
        rank.Equals(LevelManager.Instance.GetRank(score));
        bSelf = transform;
        state.Add(transform.position.x);
        state.Add(transform.position.y);
        state.Add(score);
        state.Add(lives);
     targ = FindObjectsOfType<Honeycomb>();
        foreach (Honeycomb h in targ)
        {
            if(h.open)
            {
                targActive = h;
                state.Add(targActive.transform.position.x);
                state.Add(targActive.transform.position.y);
            }
                if(transform.position.x != h.transform.position.x|| transform.position.y != h.transform.position.y)
            {
                reward = -0.1f;
            }
               
             
        }
        
        GameObject[] Beez = GameObject.FindGameObjectsWithTag("Bee");
        foreach (GameObject bee in Beez)
        {
            if (bee.activeSelf == true) {
                if (bee.transform.position.x - bSelf.position.x < 2.5|| bee.transform.position.y - bSelf.position.y < 2.5)
                {
                    reward -= .1f;
                    
                }
              
            
            }
        }
      

		return state;
	}
    int scoreGet(int s)
    {
        return score;
    }


    public override void AgentStep(float[] act)
    {
        if (brain.brainParameters.actionSpaceType == StateType.continuous)
        {
            float action_z = act[0];
            if (action_z > 2f)
            {
                action_z = 2f;
            }
            if (action_z < -2f)
            {
                action_z = -2f;
            }
           
            float action_x = act[1];
            if (action_x > 2f)
            {
                action_x = 2f;
            }
            if (action_x < -2f)
            {
                action_x = -2f;
            }
       


            if (done == false)
            {
                reward = 0.1f;
            }
        }
        else
        {
            int action = (int)act[0];
            if (action == 0 || action == 1)
            {
                reward = -1f;
            }
            if (action == 2 || action == 3)
            {
                reward = 0.1f;
            }
            if (done == false)
            {
                reward = 0.1f;
            }
        }
        if (lives ==0)
        {
            done = true;
            reward = -1f;
        }
    }
    /*
	public override void AgentReset()
	{

	}
    */
	public override void AgentOnDone()
	{
        lifeRankScore.OnBeeArrived();
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
