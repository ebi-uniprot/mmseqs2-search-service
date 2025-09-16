### Deploy RabbitMQ using helm command

``` 
helm install mmseqs oci://registry-1.docker.io/bitnamicharts/rabbitmq
```
### Get RabbitMQ password
```
kubectl get secret --namespace default mmseqs-rabbitmq -o jsonpath="{.data.rabbitmq-password}" | base64 -d
```

#### Update password in worker/values.yaml

## Deploy Worker Steps

#### Build worker docker image
```
cd worker
docker build -t worker-consumer:dev .
```

#### Load docker image in minkube
```
minikube profile list
minikube image load worker-consumer:dev --profile=<PROFILE>
```

#### Delete worker docker image from minikube if needed
```
helm uninstall worker-dev
minikube ssh --profile=minikube-local
docker rmi worker-consumer:dev
exit
```

#### Deploy worker in minikube

```
cd deployment
helm install worker-dev worker/
```

### Publish Message to task_queue to test
#### Port Forwarding
```
kubectl port-forward --namespace default svc/mmseqs-rabbitmq 15672:15672
```
#### Open RabbitMQ Management Console in browser and publish message
```
http://127.0.0.1:15672/#/
go to --> http://127.0.0.1:15672/#/queues/%2F/task_queue
Click "Publish Message"
Select Delivery Mode - Persistent
Payload: {
  "job_id": "job-12345",
  "fasta": ">sp|A0A0C5B5G6|MOTSC_HUMAN Mitochondrial-derived peptide MOTS-c OS=Homo sapiens OX=9606 GN=MT-RNR1 PE=1 SV=1\nMRWQEMGYIFYPRKLR\n>sp|A0A1B0GTW7|CIROP_HUMAN Ciliated left-right organizer metallopeptidase OS=Homo sapiens OX=9606 GN=CIROP PE=1 SV=1\nMLLLLLLLLLLPPLVLRVAASRCLHDETQKSVSLLRPPFSQLPSKSRSSSLTLPSSRDPQ\nPLRIQSCYLGDHISDGAWDPEGEGMRGGSRALAAVREATQRIQAVLAVQGPLLLSRDPAQ\nYCHAVWGDPDSPNYHRCSLLNPGYKGESCLGAKIPDTHLRGYALWPEQGPPQLVQPDGPG\nVQNTDFLLYVRVAHTSKCHQETVSLCCPGWSTAAQSQLTAALTSWAQRRGFVMLPRLCLK\nLLGSSNLPTLASQSIRITGPSVIAYAACCQLDSEDRPLAGTIVYCAQHLTSPSLSHSDIV\nMATLHELLHALGFSGQLFKKWRDCPSGFSVRENCSTRQLVTRQDEWGQLLLTTPAVSLSL\nAKHLGVSGASLGVPLEEEEGLLSSHWEARLLQGSLMTATFDGAQRTRLDPITLAAFKDSG\nWYQVNHSAAEELLWGQGSGPEFGLVTTCGTGSSDFFCTGSGLGCHYLHLDKGSCSSDPML\nEGCRMYKPLANGSECWKKENGFPAGVDNPHGEIYHPQSRCFFANLTSQLLPGDKPRHPSL\nTPHLKEAELMGRCYLHQCTGRGAYKVQVEGSPWVPCLPGKVIQIPGYYGLLFCPRGRLCQ\nTNEDINAVTSPPVSLSTPDPLFQLSLELAGPPGHSLGKEQQEGLAEAVLEALASKGGTGR\nCYFHGPSITTSLVFTVHMWKSPGCQGPSVATLHKALTLTLQKKPLEVYHGGANFTTQPSK\nLLVTSDHNPSMTHLRLSMGLCLMLLILVGVMGTTAYQKRATLPVRPSASYHSPELHSTRV\nPVRGIREV"
}
```

#### View result inside worker pod once completed
```
kubectl exec -it worker-dev-599449b785-hllc8 -- bash
cd /results/
```
### build api docker image (NB - Not Ready Yet)

```
cd api
docker build -t rest-api:dev .
```

#### build db docker image(NB - Not Ready Yet)
``` 
cd db
docker build -t db:dev .
```