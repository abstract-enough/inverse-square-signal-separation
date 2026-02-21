import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np
from scipy.optimize import least_squares
from sklearn.decomposition import PCA
import sys
import tensorflow as tf

snr_db = int(sys.argv[1]) 
distance = int(sys.argv[2])
grid = int(sys.argv[3])



tf.enable_eager_execution()

# 8 of receivers in a cube
M = grid**3
R = np.zeros(shape=(M,3))
m=0
for c0 in range(grid):
  for c1 in range(grid):
    for c2 in range(grid):
      R[m,0] = c0/grid - 0.5
      R[m,1] = c1/grid - 0.5
      R[m,2] = c2/grid - 0.5
      m = m + 1

R=R/distance/2 + 0.5

# number of sources, 10 would be a hard separation problem
N = 5

# 100 measurements over time
T = 100

# 100 ground truth source power samples
Q_target = np.random.normal(loc=0,scale=1,size=(N,T))

S_target = np.random.uniform(low=0,high=1,size=(N,3))



# 100 receieved power samples
D_target = np.zeros((M,N))
for m in range(M):
  for n in range(N):
    D_target[m,n] = np.power(np.sum(np.square(R[m,:]-S_target[n,:])),0.5)

#print("D_target",D_target)



print("Q_target",Q_target)
print("R", R)
print("S", S_target)
print("D", D_target)
print("U", np.divide(np.ones((M,N)),np.square(D_target)))

P = np.matmul(np.divide(np.ones((M,N)),np.square(D_target)),Q_target)

print("P", P)

P_power = np.mean(np.square(P))
snr = 10 ** (snr_db / 10)
noise_power = P_power / snr
channel_noise_normalized = np.random.normal(loc=0, scale=1, size=(M,T))
normalized_power = np.mean(np.square(channel_noise_normalized))
normalized_scale = normalized_power ** 0.5
noise_power_scale = noise_power ** 0.5 
channel_noise = channel_noise_normalized * noise_power_scale / normalized_scale

P = P + channel_noise

print("test")
channel_noise_power = np.mean(np.square(channel_noise))
print("channel noise power", channel_noise_power)
print("P power", P_power)
snr_test=10*np.log(P_power/channel_noise_power)/np.log(10)
print("snr test",snr_test)


#print("P",P)

# solution:


R = tf.convert_to_tensor(R)
P = tf.convert_to_tensor(P)
#def f(X_guess):
def loss_from_prediction(X_pred):
   S_vector = X_pred[0:(N*3)]
   Q_vector = X_pred[N*3:]

   #S_guess = S_vector.reshape(N,3)
   S_guess = tf.reshape(S_vector,(N,3))
   #Q_guess = Q_vector.reshape(N,T)
   Q_guess = tf.reshape(Q_vector,(N,T))

   #U_guess = np.zeros((M,N))
   #U_guess = tf.zeros((M,N))
   #for m in range(M):
      #for n in range(N):
        #U_guess[m,n] = np.power(np.sum(np.square(R[m,:]-S_guess[n,:])),-1)
        #U_guess[m,n] = tf.power(tf.reduce_sum(tf.square(R[m,:]-S_guess[n,:])),-1)
        #U_guess[m,n] = tf.pow(tf.reduce_sum(tf.square(R[m,:]-S_guess[n,:])),-1)
   U_guess = tf.pow(tf.reduce_sum(tf.square(\
     tf.tile(tf.reshape(R,(M,1,3)),(1,N,1))-\
     tf.tile(tf.reshape(S_guess,(1,N,3)),(M,1,1))),2),-1)



   #error = P-np.matmul(U_guess,Q_guess)
   #error_vector = error.reshape((M*T,))
   #return error_vector
   P_guess = tf.matmul(U_guess,Q_guess)
   return tf.reduce_sum(tf.square(P-P_guess))




# check that f(x) == 0
S_vector = S_target.reshape((N*3,))
Q_vector = Q_target.reshape((N*T,))
X_target = np.concatenate((S_vector,Q_vector))
#errors = f(X_target)
#ground truth loss nonzero due to added noise
#print("ground truth loss",0.5*np.sum(np.square(errors)))


#max_nfev = 100

X0 = np.random.normal(loc=0,scale=1,size=(N*(T+3),))
#X_guess=least_squares(fun=f,x0=X0,verbose=2)


opt = tf.keras.optimizers.Adam(learning_rate=0.001)
X_guess = tf.Variable(tf.convert_to_tensor(X0))


X_per_epoch = []
loss_per_epoch = []
loss = lambda: loss_from_prediction(X_guess)
for i in range(50000):
  step_count = opt.minimize(loss, [X_guess]).numpy()
  current_loss = loss_from_prediction(X_guess).numpy()
  loss_per_epoch.append(current_loss)
  X_per_epoch.append(X_guess.numpy())
  print(current_loss)
  
# The first step is `-learning_rate*sign(grad)`
#X_guess = X_guess.numpy()
best_epoch = loss_per_epoch.index(min(loss_per_epoch))
X_guess = X_per_epoch[best_epoch]


S_vector = X_guess[0:(N*3)]
Q_vector = X_guess[N*3:]
S_guess = S_vector.reshape(N,3)
Q_guess = Q_vector.reshape(N,T)

# check that f(x) == 0
S_guess_vector = S_guess.reshape((N*3,))
Q_guess_vector = Q_guess.reshape((N*T,))
X_guess = np.concatenate((S_vector,Q_vector))
#errors = f(X_guess)
#print("prediction loss",0.5*np.sum(np.square(errors)))

# find solution permutation
S_temp = np.zeros((N,3))
Q_temp = np.zeros((N,T))
used_indices = []
for n in range(N):
  best_score = 0
  for n_guess in range(N):
    already_used = False
    for n_used in used_indices:
      if n_guess == n_used:
        already_used = True
        break
    if not already_used:
      score = np.power(np.sum(np.square(S_target[n,:]-S_guess[n_guess,:])),-1)
      if score > best_score:
        best_score = score
        best_index = n_guess

  S_temp[n,:] = S_guess[best_index,:]
  Q_temp[n,:] = Q_guess[best_index,:]

S_guess = S_temp
Q_guess = Q_temp

rmse=np.power(np.mean(np.square(Q_guess-Q_target)),0.5)
print("rms error",rmse)

# check that f(x) == 0
S_guess_vector = S_guess.reshape((N*3,))
Q_guess_vector = Q_guess.reshape((N*T,))
X_guess = np.concatenate((S_vector,Q_vector))
#errors = f(X_guess)
#print("permuted prediction loss",0.5*np.sum(np.square(errors)))


#print solution

#print("number of iterations = ", max_nfev)
S_target_array = []
for n in range(N):
  for c in range(3):
    S_target_array.append(S_target[n,c])

S_guess_array = []
for n in range(N):
  for c in range(3):
    S_guess_array.append(S_guess[n,c])


Q_target_array = []
for n in range(N):
  for t in range(T):
    Q_target_array.append(Q_target[n,t])

Q_guess_array = []
for n in range(N):
  for t in range(T):
    Q_guess_array.append(Q_guess[n,t])


save_str = "snrdb_"+str(snr_db)+"_dist_"+str(distance)+"_grid_"+str(grid)
plt.plot(Q_target_array, label = "Source Signal Target")
plt.plot(Q_guess_array, label = "Source Signal Prediction")
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.title("Source Prediction Error all Transmitters")
plt.legend()
plt.show()
plt.savefig("Source Prediction Error all Transmitters"+str(save_str)+".png")
plt.close()


plt.plot(S_target_array, label = "Source Locations Target")
plt.plot(S_guess_array, label = "Source Locations Prediction")
plt.xlabel("All Sources and Spatial Dimensions")
plt.ylabel("Spatial Position")
plt.title("Source Locations Error all Transmitters")
plt.legend()
plt.show()
plt.savefig("Source Locations Error all Transmitters_"+str(save_str)+".png")
plt.close()

pca = PCA(n_components=2)
pca.fit(S_target)
S_guess_2D = pca.transform(S_guess)
S_target_2D = pca.transform(S_target)

for n in range(N):
  plt.scatter(x=[S_target_2D[n,0],S_guess_2D[n,0]],y=[S_target_2D[n,1],S_guess_2D[n,1]], label="Source "+str(n))
plt.xlabel("Spatial Dimension 1")
plt.ylabel("Spatial Dimension 2")
plt.title("Source Locations Error Projection in 2D Space")
plt.legend()
plt.show()
plt.savefig("Source Locations Error Projection in 2D Space_"+str(save_str)+".png")
plt.close()

for n in range(N):
  plt.plot(Q_target[n,:], label = "Source Signal Target")
  plt.plot(Q_guess[n,:], label = "Source Signal Prediction")
  plt.xlabel("Time")
  plt.ylabel("Amplitude")
  plt.title("Source "+str(n+1)+" Prediction Error")
  plt.legend()
  plt.show()
  plt.savefig("Source "+str(n+1)+" Prediction Error_"+str(save_str)+".png")
  plt.close()
