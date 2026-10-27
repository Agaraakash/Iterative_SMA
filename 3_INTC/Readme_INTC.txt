intitial iteration2 run->
	we had 73 percent loss !
Realisations->
	from period 2004 to 2008 there were massive losses !
	
Hypothesis and support->
	hypothesis 2 ->
		in iteration 2 we added an inetersection condition but we realised many times it would touch it due to noise 
		so it would make bad trades 
	fix-> my high_20 needs to decrease by 10 percent atleast for to believe it is a true indicator 
	
	so new indicator is and btw these 2 
	
	hypothesis 1 -> was just a change that needed to be mirrored in position negative too
 
by these hypothesis the training data got a 29 percent profit but standard deviation was still 33 percent 

so we looked further into main std point 2004 to 2006

realisation_again-> we notice that in maxima minima we are late to realise and because if at maxima minima fluctuations are there then
			we tend to miss them by 20 days potentially getting into loss many times 
hypothesis -> SMA_small_small of 10 days was added to tell better nature of it 
	
we named it iteration 4 and it had 10 percent only profit with 28 percent std signing trying to overfit 2004 and 2006


onto final out_sample
all iterations fail showing this data wasn't near suitable data for our SMA strategy and it might be very well possible that we cant just use indicators of one strategy and fit all data sometimes that main core of strategy follows reverse principle of strategy which might have further 
indicators but right now we limited it to SMA