The task - extract the fresh produce

Solution is to be:

- Scalable: different segmentation methods could be used easily
- Args: path to video, --output folder


### Reasoning / thoughts
The video processing pipeline could be logically split into 3 parts:
1. Read a frame from disk
2. Process the frame
3. Save the result (the mask) on disk

*Scalability*:

The steps 1 and 3 are IO bound meaning we could easily move them to separate
threads. The step 2 could be both CPU or GPU bound depending on an algorithm. 
Said that I also moved step 2 to a separate thread. The workers are connected
using queues. The main thread is not blocked meaning we could potentially
communicate to it - request video processing progress using its ID, reply
to requests etc.

As for the segmentation algorithm, there are multiple ways how the task could be
done:

a) Traditional machine vision techniques - the ones I've tried

b) Deep learning segmentation models such as Unet, Mask RCNN etc.

We want to be able to swap them easily - this is the reason why I created the
AbstractSegmenter class which defines the interface that all potential segmentation 
algorithms would have to implement to be able to get plugged into the detector.

This is a super interesting task, I can see how a segmentation neural network
could be used to solve it well. I decided to spent the majority of the time for
this task building more or less scalable solution rather than finding the best
algorithm to segment the goods.

Both of my versions of the algorithm could be found under segmenter. To run
the version 1 or 2 please change the Config attribute SEGMENT_VERSION. 

By tweaking the queue sizes we could change the performance speed/memory wise.