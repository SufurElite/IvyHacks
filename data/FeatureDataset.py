import numpy as np
import os
def read_data():

	X = []
	y = []
	STORING_PATH = os.getcwd()+'/games_data/'
	files = [STORING_PATH+"preferCnnFileEnd.txt", STORING_PATH+"preferCnnFileMiddle.txt",STORING_PATH+"preferCnnFileOpening.txt"]
	files2 = [STORING_PATH+"rejectCnnFileEnd.txt", STORING_PATH+"rejectCnnFileMiddle.txt",STORING_PATH+"rejectCnnFileOpening.txt"]
	for tmp in files:
		# Location of txt file
		with open(tmp, 'r') as f:	
			print("Reading the Data")
			try:
				for line in f:
					record = line.split(";")
					pieces = [eval(x) for x in record[0:12]]
					piece = [item for sublist in pieces for item in sublist]
					piece = [item for sublist in piece for item in sublist]	
					features = [eval(x) for x in record[12:16]]
					feature = [item for sublist in features for item in sublist]
					Evaluation = float(record[16][:-2])
					Information = np.asarray(piece + feature+[Evaluation])					
					X.append(Information)
					y.append(1)
			except:
				pass
	for tmp in files2:
		# Location of txt file
		with open(tmp, 'r') as f:	
			print("Reading the Data")
			try:
				for line in f:
					record = line.split(";")
					pieces = [eval(x) for x in record[0:12]]
					piece = [item for sublist in pieces for item in sublist]
					piece = [item for sublist in piece for item in sublist]	
					features = [eval(x) for x in record[12:16]]
					feature = [item for sublist in features for item in sublist]
					Evaluation = float(record[16][:-2])
					Information = np.asarray(piece + feature+[Evaluation])					
					X.append(Information)
					y.append(0)
			except:
				pass

	New_X = np.asarray(X)

		
	new_y = np.asarray(y)
	
	print(New_X.shape)
	print(new_y.shape)
	print(len(New_X))
	print(len(new_y))

	np.save(STORING_PATH+'CnnFeaturePositions.npy', New_X)
	np.save(STORING_PATH+'CnnFeatureTarget.npy', new_y)

def main():
        read_data()
       
if __name__ == '__main__':
	main()
