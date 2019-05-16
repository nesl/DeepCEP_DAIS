# DeepCEP: Deep Complex Event Processing Using Distributed Multimodal Information
This repo has an implemntation of our paper [DeepCEP: Deep Complex Event Processing Using Distributed Multimodal Information](https://dais-ita.org/node/3537)


## Framework Overview
DeepCEP is a framework for processing complex events with intergrated deep learning networks.
![DeepCEP](https://github.com/nesl/DeepCEP_DAIS/blob/master/Images/DeepCEP.png)
<img src="https://github.com/nesl/DeepCEP_DAIS/blob/master/Images/DeepCEP.png" width="700">
- DeepCEP consists of 2 parts: _Deep data abstractor_ and _Uncertainty Robust CEP engine_.
- _Deep data abstractor_ structure and abstract raw data into primitive events with semantic meanings.
  - _Deep data abstractor_ use YOLOv3 objection detection model: Model from [here](https://github.com/TianweiXing/YOLOv3 "YoloV3"), trained in Keras.
  - A primitive event is generated only when a "change of states" is observed.
- _Uncertainty Robust CEP engine_ is used for detect complex patterns while also calculate the probability of complex event happening:
  - CEP engine is inspired and modified from the [SASE (Eugene Wu et. al, Berkeley 2006)](http://sase.cs.umass.edu/)CEP system, implemented in python and use ProbLog,  
  - Ordered sub-list
  - Use a run-time stack to store the latest K events. (stack has fixed size. It can also be dynamic based on time window.)
- Compilier stuff... ****to be added

## Instruction
1. Create Complex Event definition file, e.g. CE_example.txt
```bash
python 
```
2. Use Compilier to read complex event definition. ****to be added
3. Setup deep learning models on data abstractors.
4. Initialize centralized CEP engine:
```bash
python server.py --argument
```
5. Add distributed data abstractor:
```bash
python device.py --argument
```


## Files:

- **Compiler**: ***to be added
- **Data_abstractor**: 
  - Obj_Detector
  - Event_generator
- **CEP_engine**:
  - sth
- **Images**
- server.py
- device.py
- requirements.txt
- License


## Maintainer
* This project is maintained by: Tianwei Xing (malzantot)

