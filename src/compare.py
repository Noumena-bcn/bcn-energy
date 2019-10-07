python_file = open ("C:/Users/Coroush/Desktop/git-noumena/bcn-energy/result/eplusout.rdd","r")
gh_file = open ("C:/Users/Coroush/Desktop/git_noumena/Comparison/gh_result5/unnamed/EnergyPlus/unnamed.rdd","r")

python = python_file.readlines()
gh = gh_file.readlines()
dif = []
for i in gh:
    if i not in python:
        dif.append(i)

print (len(dif))
diff = open ("diff.text","w")
diff.writelines(dif)