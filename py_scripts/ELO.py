import math 
from py_scripts import ACR_Globals

def EXPECTATION(P1, P2): 
	""" Calculates the 'Expectation' value following the formula provided by FIDE [https://www.fide.com/fide/handbook.html?id=172&view=article] although in this case, is more of a probability than an expectation"""
	""" if P1 has ACR_Globals.__MAX_DIFF more ELO points than P2, they are 10 times better (and should win 10/11, ~90.1% of the time). [https://blog.mackie.io/the-elo-algorithm] """
	return 1.0 / (1 + math.pow(10, -((P1 - P2) / ACR_Globals.__MAX_DIFF)))

def K_FACTOR(elo_diff, underdog_won, tries):
	if tries >= ACR_Globals.__MAX_TRIES: 
		tries = ACR_Globals.__MAX_TRIES
	if underdog_won: 	
		return ((elo_diff + ACR_Globals.__MAX_ELO) / ACR_Globals.__MAX_ELO) * (tries / ACR_Globals.__MAX_TRIES)
	else:				
		return (1 - elo_diff / ACR_Globals.__MAX_ELO) * (tries / ACR_Globals.__MAX_TRIES)

def SIMULATE(ELO_user, ELO_problem, Submission_State, tries):
	""" Calculates the new ratings for both player & problem """

	User_Old_Score = ELO_user
	Problem_Old_Score = ELO_problem

	User_Expectation = EXPECTATION(User_Old_Score, Problem_Old_Score) 
	Problem_Expectation = EXPECTATION(Problem_Old_Score, User_Old_Score) 
	ELO_Difference = User_Old_Score - Problem_Old_Score

	# If Player_1 beats Player_2
	if Submission_State in ('AC', 'PE'): 

		# If Player_1 Wins, and his score is lower than Player_2's score
		if User_Old_Score < Problem_Old_Score: 
			k = K_FACTOR(abs(ELO_Difference), True, tries)

		# If Player_1 Wins, but his score is higher than Player_2's score
		else:	
			k = K_FACTOR(abs(ELO_Difference), False, tries)
		User_New_Score = User_Old_Score + k * (1 - User_Expectation)
		Problem_New_Score = Problem_Old_Score + k * (0 - Problem_Expectation)

	# If Player_2 beats Player_1
	else : 

		# If Player_2 Wins, and his score is lower than Player_1's score
		if Problem_Old_Score < User_Old_Score: 
			k = K_FACTOR(abs(ELO_Difference), True, tries)

		# If Player_2 Wins, but his score is higher than Player_1's score
		else:	
			k = K_FACTOR(abs(ELO_Difference), False, tries)
		User_New_Score = User_Old_Score + k * (0 - User_Expectation)
		Problem_New_Score = Problem_Old_Score + k * (1 - Problem_Expectation)

	# The following statements prevent the scores from going over 16 or reaching negative values
	if User_New_Score < 0 or User_New_Score >16 or Problem_New_Score < 0 or Problem_New_Score >16: 
		User_New_Score = User_Old_Score
		Problem_New_Score = Problem_Old_Score
	
	return User_New_Score, Problem_New_Score
