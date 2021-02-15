

if __name__ == '__main__':
    rcR, rcS = Pipe(duplex = False)
    camR, camS = Pipe(duplex = False)
    embR, embS = Pipe(duplex = False)
    
    output_p = {"ENPB": embS}
    SerialHandler([rcR], [output_p]).start()
    camProc = CameraProcess([],[camS]).start()

    delay = 0.5
    right = [0.15, 20]
    left = [3.0, -20]

    rcS.send(drive(0.2, 20))
    rcS.send(enbp())



    

a[6:-2]

    while True:


        encoder_rps = float(embR.recv()[6:-2])
        speed = (2 * math.pi * 0.03) * encoder_rps 
        print ("****", speed)
        time.sleep(0.1)
