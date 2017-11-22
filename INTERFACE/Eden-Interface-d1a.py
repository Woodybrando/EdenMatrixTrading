a = 0

b = 0

c = 0

d = 0

e = 0

n = str("never!")

y = str("yes!")


a = input("Welcome back to Eden! Do u want to build a new matrix? y or n?")

print(a)

if a == y:
    invest = input("Sweet, how much fiat do you want to invest in dollars? e.g. 1000")

    print(invest)


    moonFactor = input("What percent of your investment should go in the moon bucket? e.g .15")

    print(moonFactor)

    moonBucket = invest * moonFactor

    print("Moonbucket amount: " + str(moonBucket))

    initMatrix = invest - moonBucket

    print("This much for the matrix " + str(initMatrix))

    marketPrice = input("What's the current market price? e.g. 72")

    initAbove = round(initMatrix / 2)

    initBelow = round(initMatrix - initAbove)

    count = initAbove

    moonPeg = marketPrice * 2

    print(moonPeg)

    pegValue = initAbove / 20

    print(pegValue)

    initVolume = pegValue / marketPrice

    print(initVolume)

    bottomPeg = marketPrice * .25

    while count > bottomPeg:
        matrixPeg = moonPeg * .98

        moonPeg = matrixPeg

        print(round(moonPeg, 2), pegValue, round(initVolume, 2))

        count = moonPeg
