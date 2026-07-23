import sys
import re

N = int(sys.argv[1])
file_name = f"fdr_{N}.prism"
file_name_a = f"fdr_0.59-0.61_{N}.prism"

with open(file_name, 'w') as file:
    with open(file_name_a, 'w') as file_a: # open(file_name_a, 'w') as file_a: #overwrites file if exists
        for file_x in [file, file_a]:
            file_x.write("// https://zenodo.org/records/10438916\n")
            file_x.write("// Fast Dice Roller Algorithm for uniform random sampling using coin flips [J. Lumbroso, arXiv:1304.1916, 2013]\n")
            file_x.write("// The given encoding is based on a transformation to a probabilistic program by Daniel Zilken\n")
            file_x.write("// Extended to biased coins by Lina Gerlach\n")
            file_x.write("\n")
            file_x.write("mdp\n\n")
            file_x.write(f"const int N={N}; // N > 0, the algorithm samples uniformly from {{0, ..., N-1}}\n\n")


        file.write("const double bias_l = 0.5; // lower bound for bias towards 0\n")
        file.write("const double bias_u = 0.5; // upper bound for bias towards 0\n")
        file_a.write("const double bias_l = 59/100; // lower bound for bias towards 0\n")
        file_a.write("const double bias_u = 61/100; // upper bound for bias towards 0\n")

        for file_x in [file, file_a]:
            file_x.write("\n")
            file_x.write("formula decrHeads = 2*c >= N ? N : 0;\n")
            file_x.write("formula decrTails = 2*c+1 >= N ? N : 0;\n")
            file_x.write("module main\n")
            file_x.write("    v : [0..N] init 1;\n")
            file_x.write("    c : [0..N] init 0;\n")
            file_x.write("    [l] v<N -> bias_l : (v' =min(N,2*v-decrHeads)) & (c'=2*c-decrHeads) + (1-bias_l) : (v' =min(N,2*v-decrTails)) & (c'=2*c+1-decrTails);\n")
            file_x.write("    [u] v<N -> bias_u : (v' =min(N,2*v-decrHeads)) & (c'=2*c-decrHeads) + (1-bias_u) : (v' =min(N,2*v-decrTails)) & (c'=2*c+1-decrTails);\n")
            file_x.write("    [] v=N -> 1 : true;\n")
            file_x.write("endmodule\n")
            file_x.write("\n")

            for i in range(1,2*N+1):
                file_x.write(f"label \"init{i}\" = (v=1)&(c=0);\n")
            file_x.write("\n")

            for i in range(0,N):
                file_x.write(f"label \"d{i}\" = (v=N)&(c={i});\n")
            file_x.write("\n")

## Property for RelProp
prop_file_name = f"prop_{N}.txt"
prop_file_name_a = f"prop_0.59-0.61_{N}.txt"

with open(prop_file_name, 'w') as prop_file:
    with open(prop_file_name_a, 'w') as prop_file_a:
        prop_file.write(f"--modelPath ./benchmark/FDR/{file_name} ")
        prop_file_a.write(f"--modelPath ./benchmark/FDR/{file_name_a} ")
        for prop_file_x in [prop_file, prop_file_a]:
            prop_file_x.write(f"--numPred {N} --numInit {2*N} --numScheds 1 ")
            prop_file_x.write("--schedList ")
            for i in range(2*N):
                prop_file_x.write("1 ")
            prop_file_x.write("--targets ")
            for i in range(N-1):
                prop_file_x.write(f"d{i} d{i+1} ")
            prop_file_x.write(f"d{N-1} d0 ")
            prop_file_x.write("--coefficient ")
            for i in range(N):
                prop_file_x.write("1 -1 0 ")
            prop_file_x.write("-cop !=")

## Property for HyperProb
prop_file_name = f"prop_HyperProb_{N}.txt"
prop_file_name_eps = f"prop_HyperProb_eps_{N}.txt"

disjuncts=[]
disjuncts_eps=[]
for i in range(N-1):
    disjuncts.append(f"((P(F d{i}(s1)) < P(F d{i+1}(s1))) | (P(F d{i}(s1)) > P(F d{i+1}(s1))))")
    disjuncts_eps.append(f"((P(F d{i}(s1)) < P(F d{i+1}(s1)) - 0.13 ) | (P(F d{i}(s1)) > P(F d{i+1}(s1)) + 0.13))")
disjuncts.append(f"((P(F d{N-1}(s1)) < P(F d0(s1))) | (P(F d{N-1}(s1)) > P(F d0(s1))))")
disjuncts_eps.append(f"((P(F d{i}(s1)) < P(F d{i+1}(s1)) - 0.13 ) | (P(F d{i}(s1)) > P(F d{i+1}(s1)) + 0.13 ))")

with open(prop_file_name, 'w') as prop_file:
    with open(prop_file_name_eps, 'w') as prop_file_eps:
        for prop_file_x in [prop_file, prop_file_eps]:
            prop_file_x.write("AS sh . A s1 . (init1(s1) -> ")
            for i in range(N-1):
                prop_file_x.write("(")

        prop_file.write(disjuncts[0])
        for i in range(1,N):
            prop_file.write(f" | {disjuncts[i]})")

        prop_file_eps.write(disjuncts_eps[0])
        for i in range(1,N):
            prop_file_eps.write(f" | {disjuncts_eps[i]})")

        for prop_file_x in [prop_file, prop_file_eps]:
            prop_file_x.write(" )")

## Property for HyperPAYNT
# Syntax: "bound -- P1 op P2" means "P1 + bound op P2"
prop_file_name = f"sketch_{N}.props"
prop_file_name_eps = f"sketch_eps_{N}.props"

with open(prop_file_name, 'w') as prop_file:
    with open(prop_file_name_eps, 'w') as prop_file_eps:
        for prop_file_x in [prop_file, prop_file_eps]:
            prop_file_x.write("ES sched1\n")
            prop_file_x.write("E s0(sched1)\n")
            prop_file_x.write("Restrict s0 init1\n")

        for i in range(N-1):
            prop_file.write(f"P{{s0}}[F \"d{i}\"] <= P{{s0}}[F \"d{i+1}\"]\n")
            prop_file.write(f"P{{s0}}[F \"d{i+1}\"] <= P{{s0}}[F \"d{i}\"]\n")
        prop_file.write(f"P{{s0}}[F \"d{N-1}\"] <= P{{s0}}[F \"d{0}\"]\n")
        prop_file.write(f"P{{s0}}[F \"d{0}\"] <= P{{s0}}[F \"d{N-1}\"]\n")

        for i in range(N-1):
            prop_file_eps.write(f"-0.13 -- P{{s0}}[F \"d{i}\"] <= P{{s0}}[F \"d{i+1}\"]\n")
            prop_file_eps.write(f"-0.13 -- P{{s0}}[F \"d{i+1}\"] <= P{{s0}}[F \"d{i}\"]\n")
        prop_file_eps.write(f"-0.13 -- P{{s0}}[F \"d{N-1}\"] <= P{{s0}}[F \"d{0}\"]\n")
        prop_file_eps.write(f"-0.13 -- P{{s0}}[F \"d{0}\"] <= P{{s0}}[F \"d{N-1}\"]\n")
