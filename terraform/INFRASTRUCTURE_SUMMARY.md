# 📋 RESUMEN DE INFRAESTRUCTURA AWS - Merval Inteligente

## 🌐 Configuración General

**Región:** `us-east-1` (Norte de Virginia)
**VPC ID:** `vpc-075ea12c12e95bae0`
**Subnet ID:** `subnet-0b69dcddae1c49d91`
**Key Pair:** `millaveuade`

---

## 🖥️ Instancias EC2 Existentes

### 1. general-general
- **Instance ID:** `i-0e4c1d12b4ff552d1`
- **Tipo:** `t3.micro`
- **Estado:** `running`
- **IP Pública:** `52.91.19.181`
- **IP Privada:** `10.0.1.142`
- **Security Groups:** 
  - `sg-012d0c1b7a70ba81f` (alertas-public-sg)
  - `sg-0efd45a3dff64e09f` (alertas-internal-sg)

### 2. alertas-api
- **Instance ID:** `i-00aecd8bc040359b2`
- **Tipo:** `t3.micro`
- **Estado:** `running`
- **IP Pública:** `13.222.61.10`
- **IP Privada:** `10.0.1.94`
- **Security Groups:** 
  - `sg-012d0c1b7a70ba81f` (alertas-public-sg)
  - `sg-0efd45a3dff64e09f` (alertas-internal-sg)

### 3. chat-chat
- **Instance ID:** `i-00a82c02353f450b3`
- **Tipo:** `t3.micro`
- **Estado:** `running`
- **IP Pública:** `13.220.110.105`
- **IP Privada:** `10.0.1.148`
- **Security Groups:** 
  - `sg-0efd45a3dff64e09f` (alertas-internal-sg)
  - `sg-01f7d11a5162691a0` (chat-chat-sg)

---

## 🔒 Security Groups

### sg-012d0c1b7a70ba81f - alertas-public-sg ⭐ RECOMENDADO
**Descripción:** Security group for public HTTP access
**VPC:** `vpc-075ea12c12e95bae0`

**Reglas de Ingreso:**
- ✅ **Puerto 22 (SSH)** - De: `0.0.0.0/0` (Público)
- ✅ **Puerto 80 (HTTP)** - De: `0.0.0.0/0` (Público)
- ✅ **Puerto 5000** - Comunicación interna VPC
- ✅ **Puerto 8000** - Comunicación interna VPC
- ✅ **Puerto 8080** - Comunicación interna VPC

**✨ PERFECTO para la API Sentiment (puerto 8001)**
- Ya tiene SSH habilitado
- Ya tiene puertos HTTP configurados
- Compatible con la API en puerto 8001

### sg-0efd45a3dff64e09f - alertas-internal-sg
**Descripción:** Security group for internal VPC communication
**VPC:** `vpc-075ea12c12e95bae0`

**Reglas de Ingreso:**
- ✅ **Todo el tráfico TCP** - De: `10.0.0.0/16` (Solo interno VPC)

### sg-01f7d11a5162691a0 - chat-chat-sg
**Descripción:** HTTP 80 publico + intra-VPC
**VPC:** `vpc-075ea12c12e95bae0`

**Reglas de Ingreso:**
- ✅ **Puerto 22 (SSH)** - De: `0.0.0.0/0` (Público)
- ✅ **Puerto 80 (HTTP)** - De: `0.0.0.0/0` (Público)
- ✅ **Todo el tráfico TCP** - De: `10.0.0.0/8` (Rango interno amplio)

---

## 🎯 Recomendación para Sentiment API

### Opción 1: Usar Security Group Existente ✅ RECOMENDADO

**Security Group:** `sg-012d0c1b7a70ba81f` (alertas-public-sg)

**Ventajas:**
- ✅ Ya configurado con múltiples puertos
- ✅ Usado por tus otras APIs (general-general, alertas-api)
- ✅ SSH ya habilitado
- ✅ Puertos 8000, 8080, 5000 ya abiertos

**Acción requerida:**
Agregar puerto 8001 al Security Group:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-012d0c1b7a70ba81f \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0
```

### Opción 2: Usar ambos Security Groups

Combinar:
- `sg-012d0c1b7a70ba81f` (alertas-public-sg) - Acceso público
- `sg-0efd45a3dff64e09f` (alertas-internal-sg) - Comunicación interna VPC

**Ventaja:** 
- Permite comunicación con otras instancias en el VPC
- Mantiene acceso público

---

## 📝 Configuración de Terraform

Ya he actualizado `terraform.tfvars.example` con estos valores:

```hcl
aws_region        = "us-east-1"
vpc_id            = "vpc-075ea12c12e95bae0"
subnet_id         = "subnet-0b69dcddae1c49d91"
security_group_id = "sg-012d0c1b7a70ba81f"
key_name          = "millaveuade"
instance_type     = "t3.micro"
```

---

## 🚀 Próximos Pasos

### 1. Agregar puerto 8001 al Security Group

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-012d0c1b7a70ba81f \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0 \
  --region us-east-1
```

### 2. Crear archivos de configuración

```bash
cd terraform
Copy-Item terraform.tfvars.example terraform.tfvars
Copy-Item sensitive.tfvars.example sensitive.tfvars
```

### 3. Editar sensitive.tfvars con tus credenciales MongoDB

```hcl
mongodb_uri   = "mongodb+srv://admin:tRVIi8NhbKbzDj0q@cluster0.dad6cgj.mongodb.net/MervalDB?retryWrites=true&w=majority"
database_name = "MervalDB"
db_port       = "27017"
```

### 4. Deploy con Terraform

```bash
terraform init
terraform plan -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
terraform apply -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
```

---

## 💰 Costos Estimados

Con **t3.micro** (actual en tus instancias):
- Instancia EC2 t3.micro: ~$7.50/mes
- EBS 20GB gp3: ~$2/mes
- **Total: ~$9.50/mes**

Actualmente tienes 3 instancias t3.micro, esta sería la 4ta.

---

## 📞 Comandos Útiles

### Ver estado de todas las instancias
```bash
aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,Tags[?Key==`Name`].Value|[0],State.Name,PublicIpAddress]' --output table
```

### Ver reglas de un Security Group
```bash
aws ec2 describe-security-groups --group-ids sg-012d0c1b7a70ba81f --query 'SecurityGroups[].IpPermissions[]' --output table
```

### SSH a la nueva instancia (después del deploy)
```bash
ssh -i ~/.ssh/millaveuade.pem ec2-user@<IP_PUBLICA>
```
