import configuration

max = int(configuration.time_test)
#stampa quello che dobbiamo scrivere sotto operations sul file yaml  client.yaml
for x in range(5, max-5, 5):
    if x % 2 == 0:
        print("  - \"" + str(x) + " SCALE 1\"")
    else:
        print("  - \"" + str(x) + " SCALE 0\"")

