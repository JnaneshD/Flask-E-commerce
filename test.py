
from profanity_check import predict, predict_prob
import enchant
import string
from nltk.corpus import stopwords
from nltk import FreqDist


stopwords_english = stopwords.words('english')

d = enchant.Dict("en_US")

msg="The product really sucks. i bought it two months ago its already not working . Guys dont buy this product . worst product in the history of mankind fuck this shit asshole insane kick your ass"

msg="too good good good too good too good too good too good bad bad bad bad bad bad bad bad bad sd sd fs dfs d ad a wsd awsda wdawsd"

stopwords = [word for word in msg.split() if word not in stopwords_english]

stop_words=[word.lower() for word in stopwords if word not in string.punctuation]

fr=FreqDist(stop_words)
point=0
print(fr.most_common(10))
bad_point=0
good_point=0
if(len(fr.most_common(10))<3):
	print("Spam")
for key,v in fr.most_common(10):
	if(v>20):
		print("Spam review")
	if(key=="bad"):
		bad_point=bad_point+1
	if(key=="good"):
		good_point=good_point+1
if(good_point and bad_point):
	print("It cant be true")
t=0
f=0
total=0
true_words=[]
for i in stop_words:
	total=total+1
	if(d.check(i)==True):
		t=t+1
		true_words.append(i)
	else:
		f=f+1
if((t/total)<0.5):
	point=point+1
	print("Fake review")
print(t/total)
x=predict_prob(true_words)
for n in x:	
	if(n>0.75):
		print(n)
bad_word_rate = sum(x)/len(x)
if(bad_word_rate>0.6):
	print("Using bad words")