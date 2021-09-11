def show_clustering(fignumber,Y,image_paths, label_pred):
     def on_press(event):
         print('you pressed', event.button, event.xdata, event.ydata)
         if not event.button==2:
             return

         dists = Y - np.array([event.xdata, event.ydata])

         dists = np.sum(dists**2,axis=1)
         print(np.argmin(dists), np.min(dists))

         closest_point_index = np.argmin(dists)

         print(image_paths[closest_point_index])
         [head, tif_filename] = 
os.path.split(image_paths[closest_point_index])

         img = cv2.imread(image_paths[closest_point_index])

         fig = plt.figure(fignumber+1)
         plt.clf()
         plt.imshow(img[::-1, :,:], cmap='gray')#rotado porque los tifs 
sino quedan mal
         plt.title('#%d, %s, class = %d' % (closest_point_index, 
tif_filename, label_pred[closest_point_index]) )
         fig.canvas.draw()
         fig.canvas.flush_events()

     fig = plt.figure(fignumber)
     plt.clf()
     plt.scatter(Y[:, 0], Y[:, 1], c=label_pred)
     plt.title("Clustering")
     plt.set_cmap('jet')


     # connect the 'on_press' event
     cid = fig.canvas.mpl_connect('button_press_event', on_press)

