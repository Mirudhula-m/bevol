# bevol

### Sequence evolution simulator for in-silico experimentation.

Conducting physical experiments in order to analyze sequence evolution requires a considerable amount of time and resources. The purpose of our project will be to construct an in silico experimentation tool to test scenarios of sequence evolution to better our understanding of evolutionary sequence effects.

We started from a binarized sequence of genes, which was converted to transcripts and then translated into proteins. We quantified the effect of each protein and their contribution to the overall fitness of the organism by computing certain cellular processes. This way the resulting protein sequences was evaluated for their phenotypic fitness, which later helped us determine whether the individual bacteria gets selected or not. After an additional step to introduce random mutations, the new set of offsprings get passed onto the next generation/epoch, where the same steps are repeated. This method is closely based on another in-silico platform called Aevol, referenced in our report. Every generation in the simulator corresponds to several bacterial generations. Our case study on this developed simulator explains how a reduced genome size is selected under high selective pressure environments like in genetic drifts, bottlenecks, etc.

In order to run the code, simply clone the repository and change the parameters section in bevol.py to fit your needs.
