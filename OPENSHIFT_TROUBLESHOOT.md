# OpenShift Route Troubleshooting Guide

## Managed Platform Plus (MPP) Internal Routing

This document captures the troubleshooting steps and solutions for configuring internal routes on OpenShift Managed Platform Plus.

### Issue: Application Not Accessible via Internal Route

**Symptoms:**
- Browser shows "Application is not available"
- Route appears configured correctly in OpenShift console
- `curl` from terminal works but browser access fails

### Root Cause: Incorrect Route Configuration for MPP

The issue was using standard OpenShift route configuration instead of Managed Platform Plus (MPP) specific configuration.

### Solution: MPP-Compliant Internal Route Configuration

According to OpenShift MPP documentation, internal shard routes require:

1. **Simplified hostname pattern**: `<app-name>.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com`
2. **Required shard label**: `shard: internal`
3. **TLS configuration**: Must include `termination: edge` with `insecureEdgeTerminationPolicy: Redirect`

#### Working Route Configuration:

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: idea-hub
  labels:
    shard: internal
spec:
  host: idea-hub.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com
  to:
    kind: Service
    name: idea-hub
  port:
    targetPort: 8080
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  wildcardPolicy: None
```

### Key Differences from Standard OpenShift

| Aspect | Standard OpenShift | Managed Platform Plus |
|--------|-------------------|------------------------|
| Hostname | Long complex names | Simplified: `<app>.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com` |
| Shard Label | Optional | **Required**: `shard: internal` |
| TLS | Optional for internal | **Required**: `termination: edge` |
| SSL Policy | Can be disabled | **Must use**: `insecureEdgeTerminationPolicy: Redirect` |

### Troubleshooting Steps

1. **Check MPP Documentation**: Always refer to the latest MPP router shard comparison table
2. **Verify shard label**: Ensure `shard: internal` is present in route metadata
3. **Use correct hostname pattern**: Simplified format, not the long cluster-specific names
4. **Include TLS configuration**: Even for "internal" routes, TLS termination is required
5. **Test with curl**: Use `curl -k` flag to bypass SSL certificate validation for testing

### Commands Used

```bash
# Delete existing route
oc delete route <route-name>

# Apply MPP-compliant route
oc apply -f route-internal.yaml

# Verify route status
oc describe route <route-name>

# Test connectivity (bypass SSL validation)
curl -k -I "https://<hostname>/"
```

### Final Working URL Format

```
https://idea-hub.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com
```

### Lessons Learned

1. **MPP has different requirements** than standard OpenShift for internal routing
2. **Always include TLS configuration** even for internal routes
3. **Shard labels are mandatory** for proper router targeting
4. **Hostname patterns must follow MPP specifications** (simplified format)
5. **Self-signed certificates are expected** for internal routes (use `-k` with curl for testing)

### Image Deployment Notes

When deploying updated Docker images:

1. **Push to Quay first**: Ensure the latest image is available in the registry
2. **Fresh deployment**: Sometimes requires deleting and recreating the app
3. **ImageStream tagging**: Use `oc tag` to point to the correct image SHA
4. **Rollout verification**: Check that pods are using the updated image

### Related Issues

- **DNS Resolution**: Internal domains may not resolve from all networks
- **SSL Certificates**: Self-signed certificates are normal for internal routes
- **Browser vs Terminal**: Browser DNS resolution may differ from terminal/curl

---
*Last Updated: August 13, 2025*
*Environment: OpenShift Managed Platform Plus (MPP)*
