# Summon messages for Lev's Quizbowl Bot
# Author: Lev Bernstein
# Version: 1.0.5
# This file just consists of the summon messages for !summon. For the actual meat of the bot's code, see QBBot.py.

import random as random

def summon():
    reports = [
        "@everyone And I saw the seven angels which stood before God; and to them were given seven trumpets.\nAnd another angel came and stood at the altar, having a golden censer; and there was given unto him much incense, that he should offer it with the prayers of all saints upon the golden altar which was before the throne.\nAnd the smoke of the incense, which came with the prayers of the saints, ascended up before God out of the angel's hand.\nAnd the angel took the censer, and filled it with fire of the altar, and cast it into the earth: and there were voices, and thunderings, and lightnings, and an earthquake.\nAnd the seven angels which had the seven trumpets prepared themselves to sound: *IT IS TIME FOR QUIZ BOWL PRACTICE.*\nText is: Revelation 8:2-6.",
        
        "@everyone Let us go then, you and I,\nWhen the evening is spread out against the sky\nLike a patient etherized upon a table;\nLet us go, through certain half-deserted streets,\nThe muttering retreats\nOf restless nights in one-night cheap hotels\nAnd sawdust restaurants with oyster-shells:\nStreets that follow like a tedious argument\nOf insidious intent\nTo lead you to an overwhelming question ...\nOh, do not ask, “What is it?”\nBecause it's obviously time for Quiz Bowl practice.\nText is: The Love Song of J. Alfred Prufrock, T. S. Eliot.",
        
        "The car's on fire, and there's no driver at the wheel/And the sewers are all muddied with a thousand lonely suicides/And a dark wind blows\nThe government is corrupt/And we're on so many drugs/With the radio on and the curtains drawn\nWe're trapped in the belly of this horrible machine/And the machine is bleeding to death\nThe sun has fallen down/And the billboards are all leering/And the flags are all dead at the top of their poles\nIt went like this:\nThe buildings toppled in on themselves/Mothers clutching babies/Picked through the rubble/And pulled out their hair\nThe skyline was beautiful on fire/All twisted metal stretching upwards/Everything washed in a thin orange haze\nI said, \"Kiss me, you're beautiful -/These are truly the last days\"\nYou grabbed my hand/And we fell into it/Like a daydream/Or a fever\nWe woke up one morning and fell a little further down/For sure it's the valley of death\nI open up my wallet/And it's full of blood\nAnyway, it's time for Quiz Bowl practice @everyone \nText is: Dead Flag Blues, Godspeed You! Black Emperor.",
        
        "Open here I flung the shutter, when, with many a flirt and flutter,\nIn there stepped a stately Raven of the saintly days of yore;\nNot the least obeisance made he; not a minute stopped or stayed he;\nBut, with mien of lord or lady, perched above my chamber door—\nPerched upon a bust of Pallas just above my chamber door—\nPerched, and sat, and nothing more.\n\nThen this ebony bird beguiling my sad fancy into smiling,\nBy the grave and stern decorum of the countenance it wore,\n“Though thy crest be shorn and shaven, thou,” I said, “art sure no craven,\nGhastly grim and ancient Raven wandering from the Nightly shore—\nTell me what thy lordly name is on the Night’s Plutonian shore!”\nQuoth the Raven “@everyone It is time for Quiz Bowl practice.”\nText is: The Raven, Edgar Allen Poe.",
        
        "The sea is calm tonight.\nThe tide is full, the moon lies fair\nUpon the straits; on the French coast the light\nGleams and is gone; the cliffs of England stand,\nGlimmering and vast, out in the tranquil bay.\nCome to the window, sweet is the night-air!\nOnly, from the long line of spray\nWhere the sea meets the moon-blanched land,\nListen! you hear the grating roar\nOf pebbles which the waves draw back, and fling,\nAt their return, up the high strand,\nBegin, and cease, and then again begin,\nWith tremulous cadence slow, and bring\nThe eternal note of practice in.\nBecause @everyone it's time for Quiz Bowl practice.\nText is: Dover Beach, Matthew Arnold.",
        
        "So there stood Matthew Arnold and this girl\nWith the cliffs of England crumbling away behind them,\nAnd he said to her, \"Try to be true to me,\nAnd I'll do the same for you, for things are bad\nAll over, but you should definitely take the time to go to Quiz Bowl practice.\nIn fact, @everyone should probably come to practice right now.\"\nText is: The Dover Bitch, Anthony Hecht.",
        
        "Rise like Lions after slumber\nIn unvanquishable number,\nShake your chains to earth like dew\nWhich in sleep had fallen on you --\nYe are many -- they are few.\nAnd @everyone it's time for Quiz Bowl practice, too.\nText is: The Masque of Anarchy, Percy Bysshe Shelley.",
        
        "He saw three high-seats, each above the other, and three men sat thereon,-one on each. And he asked what might be the name of those lords. He who had conducted him in answered that the one who sat on the nethermost high-seat was a king, \"and his name is High but the next is named Just-as-High; and he who is uppermost is called Third.\" Then Hárr asked the newcomer whether his errand were more than for the meat and drink which were always at his command, as for every one there in the Hall of the High One. He answered that he first desired to learn whether there were any wise man there within. Hárr said that he should not escape whole from thence unless he were wiser, and to prove it he should go to Quiz Bowl practice. In fact, @everyone should come to practice.\nText is: Gylfaginning, Snorri Sturluson.",
        
        "Beneath those rugged elms, that yew-tree's shade,\nWhere heaves the turf in many a mould'ring heap,\nEach in his narrow cell for ever laid,\nThe rude forefathers of the hamlet sleep.\n\nThe breezy call of incense-breathing Morn,\nThe swallow twitt'ring from the straw-built shed,\nThe cock's shrill clarion, or the echoing horn,\nNo more shall rouse them from their lowly bed.\nBut pinging them should work.\n@everyone it's time for Quiz Bowl practice.\nText is: Elegy Written in a Country Churchyard, Thomas Gray.",
        
        "Friends, Romans, countrymen, lend me your ears;\nI come to ping you, not to bother you.\nThe evil that men do lives after them;\nThe good is oft interred with their bones;\nSo let it be with pinging you.\nFor @everyone it is time for Quiz Bowl practice, and you must be alerted.\nText is: Excerpt from Julius Caesar, William Shakespeare.",
        
        "I long thought, where\nthe tiger on the street came from.\nI thought & thought,\nThought & thought\nThought & thought\nThought & thought\nAnd at that time the wind blew\nAnd I forgot what I was thinking about.\nAnd so I don't know\nwhere the tiger on the street came from.\nPerhaps I should stop pondering that and go to Quiz Bowl practice; in fact, @everyone it's time for practice.\nText is: Тигр на улице, Даниил Хармс, tr. Van Holthenrichs.",
        
        "Dearest creature in creation\nStudying English pronunciation,\nI will teach you in my verse\nSounds like corpse, corps, horse and worse.\n\nSword and sward, retain and Britain\n(Mind the latter how it's written).\nMade has not the sound of bade,\nSay-said, pay-paid, laid but plaid.\n\nDon't you think so, reader, rather,\nSaying lather, bather, father?\nFinally, which rhymes with enough,\nThough, through, bough, cough, hough, sough, tough??\n\nHiccough has the sound of sup...\nMy advice is: GIVE IT UP! Play Quiz Bowl instead. @everyone should, in fact, because it's time for practice.\nText is: The Chaos, Gerard Nolst Trenite.",
        
        "Smoke rises vertically\nSmoke drifts with air\nWeather vanes active, wind felt on face, leaves rustle\nTwigs move, light flags extend\nBranches sway, dust & loose paper blows about\nSmall trees sway, waves break on inland waters\nLarge branches sway, umbrellas difficult to use\nWhole trees sway\nTwigs broken off trees, walking made difficult\nShingles blown off roof\nTrees uprooted, damage to buildings\nWidespread damage, very rare occurrence\nViolent destruction.\n\nToday's Quiz Bowl practice brought to you by the Beaufort Wind Scale @everyone.",
        
        "What sphinx of cement and aluminum bashed open their skulls and ate up their brains and imagination?\nMoloch! Solitude! Filth! Ugliness! Ashcans and unobtainable dollars! Children screaming under the stairways! Boys sobbing in armies! Old men weeping in the parks!\nMoloch! Moloch! Nightmare of Moloch! Moloch the loveless! Mental Moloch! Moloch the heavy judger of men!\nMoloch whose mind is pure machinery! Moloch whose blood is running money! Moloch whose fingers are ten armies! Moloch whose breast is a cannibal dynamo! Moloch whose ear is a smoking tomb!\nMoloch whose eyes are a thousand blind windows! Moloch whose skyscrapers stand in the long streets like endless Jehovahs! Moloch whose factories dream and croak in the fog! Moloch whose smoke-stacks and antennae crown the cities!\nMoloch! Mol--och, excuse me, I had something in my throat. @everyone it's time for Quiz Bowl practice.\nText is: Howl, Allen Ginsberg.",
        
        "The rat men accused me of not liking stench, of not liking garbage, of not liking their squeals\nOf not liking to eat dirt!\nFor days they argued, considering the question from every angle\nFinally, they condemned me.\nYou don't like stench! You don't like garbage, you don't like our squeals! You don't like to eat dirt!\nPerhaps you'd be better off at Quiz Bowl practice. @everyone it's time for practice right now, in fact.\nText is: Nightmare, Hanns Eisler.",
        
        "Behold the chariot of the Fairy Queen!\nCelestial coursers paw the unyielding air;\nTheir filmy pennons at her word they furl,\nAnd stop obedient to the reins of light;\nThese the Queen of Spells drew in;\nShe spread a charm around the spot,\nAnd, leaning graceful from the ethereal car,\nLong did she gaze, and silently,\nshe pinged @everyone, saying,\n\"It is time for Quiz Bowl practice.\"\nText is: Queen Mab, Percy Bysshe Shelley."
        ]
    return random.choice(reports)
