// Render actual shader frames using Direct3D 11's CPU device. No interactive editor or GPU is required.
#include <windows.h>
#include <d3d11.h>
#include <d3dcompiler.h>
#include <wrl/client.h>
#include <io.h>
#include <fcntl.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <stdexcept>
#include <vector>
using Microsoft::WRL::ComPtr;
static void check(HRESULT hr){if(FAILED(hr))throw std::runtime_error("Direct3D call failed");}
static ComPtr<ID3DBlob> compile(const wchar_t* path,const char* entry,const char* version){
    ComPtr<ID3DBlob> shader,errors;
    HRESULT hr=D3DCompileFromFile(path,nullptr,nullptr,entry,version,D3DCOMPILE_ENABLE_STRICTNESS|D3DCOMPILE_OPTIMIZATION_LEVEL3,0,&shader,&errors);
    if(FAILED(hr)&&errors)std::fwrite(errors->GetBufferPointer(),1,errors->GetBufferSize(),stderr);
    check(hr);return shader;
}
struct Point{float x,y,z;};
static Point surface(int j,int i,int rings,int segments){
    double lat=-1.5707963267948966+3.141592653589793*j/rings, lon=6.283185307179586*i/segments+.14;
    return {(float)(cos(lat)*sin(lon)),(float)sin(lat),(float)(cos(lat)*cos(lon))};
}
int wmain(int argc,wchar_t** argv) {
    try{
        if(argc!=6)throw std::runtime_error("arguments: shader, scene, frames, sweep start and end frames");
        const int w=852,h=480,mode=_wtoi(argv[2]),frames=_wtoi(argv[3]),first=_wtoi(argv[4]),last=_wtoi(argv[5]);
        if(frames<1||first>=last)throw std::runtime_error("Invalid clock");
        _setmode(_fileno(stdout),_O_BINARY);std::setvbuf(stdout,nullptr,_IOFBF,1024*1024);
        ComPtr<ID3D11Device> dev;ComPtr<ID3D11DeviceContext> ctx;
        const D3D_FEATURE_LEVEL requested=D3D_FEATURE_LEVEL_11_0;
        check(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,&requested,1,D3D11_SDK_VERSION,&dev,nullptr,&ctx));
        auto vs=compile(argv[1],"SphereVS","vs_5_0"),ps=compile(argv[1],"SpherePS","ps_5_0");
        auto vs2=compile(argv[1],"PlaneVS","vs_5_0"),ps2=compile(argv[1],"GaugePS","ps_5_0");
        ComPtr<ID3D11VertexShader> meshVS,planeVS;ComPtr<ID3D11PixelShader> meshPS,gaugePS;
        check(dev->CreateVertexShader(vs->GetBufferPointer(),vs->GetBufferSize(),nullptr,&meshVS));check(dev->CreatePixelShader(ps->GetBufferPointer(),ps->GetBufferSize(),nullptr,&meshPS));
        check(dev->CreateVertexShader(vs2->GetBufferPointer(),vs2->GetBufferSize(),nullptr,&planeVS));check(dev->CreatePixelShader(ps2->GetBufferPointer(),ps2->GetBufferSize(),nullptr,&gaugePS));
        D3D11_INPUT_ELEMENT_DESC ed={"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0};ComPtr<ID3D11InputLayout> layout;
        check(dev->CreateInputLayout(&ed,1,vs->GetBufferPointer(),vs->GetBufferSize(),&layout));
        std::vector<Point> pts;int rings=(mode==42||mode==41)?12:40,segments=(mode==42||mode==41)?18:64;
        for(int j=0;j<rings;j++)for(int i=0;i<segments;i++){
            auto a=surface(j,i,rings,segments),b=surface(j,i+1,rings,segments),c=surface(j+1,i,rings,segments),d=surface(j+1,i+1,rings,segments);
            pts.insert(pts.end(),{a,b,c,c,b,d});
        }
        D3D11_BUFFER_DESC vb={};vb.ByteWidth=(UINT)(pts.size()*sizeof(Point));vb.Usage=D3D11_USAGE_IMMUTABLE;vb.BindFlags=D3D11_BIND_VERTEX_BUFFER;
        D3D11_SUBRESOURCE_DATA data={pts.data(),0,0};ComPtr<ID3D11Buffer> vertices,uniform;
        check(dev->CreateBuffer(&vb,&data,&vertices));D3D11_BUFFER_DESC cb={};cb.ByteWidth=16;cb.BindFlags=D3D11_BIND_CONSTANT_BUFFER;check(dev->CreateBuffer(&cb,nullptr,&uniform));
        D3D11_TEXTURE2D_DESC tex={};tex.Width=w;tex.Height=h;tex.MipLevels=tex.ArraySize=tex.SampleDesc.Count=1;tex.Format=DXGI_FORMAT_B8G8R8A8_UNORM;tex.BindFlags=D3D11_BIND_RENDER_TARGET;
        ComPtr<ID3D11Texture2D> target,staging,depth;ComPtr<ID3D11RenderTargetView> rtv;ComPtr<ID3D11DepthStencilView> dsv;
        check(dev->CreateTexture2D(&tex,nullptr,&target));check(dev->CreateRenderTargetView(target.Get(),nullptr,&rtv));
        tex.BindFlags=D3D11_BIND_DEPTH_STENCIL;tex.Format=DXGI_FORMAT_D32_FLOAT;check(dev->CreateTexture2D(&tex,nullptr,&depth));check(dev->CreateDepthStencilView(depth.Get(),nullptr,&dsv));
        tex.BindFlags=0;tex.Format=DXGI_FORMAT_B8G8R8A8_UNORM;tex.Usage=D3D11_USAGE_STAGING;tex.CPUAccessFlags=D3D11_CPU_ACCESS_READ;check(dev->CreateTexture2D(&tex,nullptr,&staging));
        D3D11_RASTERIZER_DESC rd={};rd.FillMode=D3D11_FILL_SOLID;rd.CullMode=D3D11_CULL_NONE;rd.DepthClipEnable=TRUE;ComPtr<ID3D11RasterizerState> rs;check(dev->CreateRasterizerState(&rd,&rs));ctx->RSSetState(rs.Get());
        D3D11_VIEWPORT viewport={0,0,(float)w,(float)h,0,1};ctx->RSSetViewports(1,&viewport);ctx->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
        UINT stride=sizeof(Point),off=0;ctx->IASetVertexBuffers(0,1,vertices.GetAddressOf(),&stride,&off);ctx->VSSetConstantBuffers(0,1,uniform.GetAddressOf());ctx->PSSetConstantBuffers(0,1,uniform.GetAddressOf());
        std::vector<unsigned char> buffer(w*h*4);float previous=-1;
        for(int frame=0;frame<frames;frame++){
            float u=std::clamp((float)(frame-first)/(last-first),0.f,1.f);
            if(u!=previous){
                previous=u;float parameters[]={u,(float)mode,(float)w,(float)h};ctx->UpdateSubresource(uniform.Get(),0,nullptr,parameters,0,0);
                const float bg[]={8/255.f,11/255.f,14/255.f,1};ctx->ClearRenderTargetView(rtv.Get(),bg);ctx->ClearDepthStencilView(dsv.Get(),D3D11_CLEAR_DEPTH,1,0);
                ctx->OMSetRenderTargets(1,rtv.GetAddressOf(),dsv.Get());
                if(mode!=39){ctx->IASetInputLayout(layout.Get());ctx->VSSetShader(meshVS.Get(),nullptr,0);ctx->PSSetShader(meshPS.Get(),nullptr,0);ctx->DrawInstanced((UINT)pts.size(),(mode==42||mode==30)?2:1,0,0);}
                ctx->OMSetRenderTargets(1,rtv.GetAddressOf(),nullptr);ctx->IASetInputLayout(nullptr);ctx->VSSetShader(planeVS.Get(),nullptr,0);ctx->PSSetShader(gaugePS.Get(),nullptr,0);ctx->Draw(3,0);
                ctx->CopyResource(staging.Get(),target.Get());D3D11_MAPPED_SUBRESOURCE map;check(ctx->Map(staging.Get(),0,D3D11_MAP_READ,0,&map));
                for(int y=0;y<h;y++)std::memcpy(buffer.data()+y*w*4,(char*)map.pData+y*map.RowPitch,w*4);
                ctx->Unmap(staging.Get(),0);
            }
            if(std::fwrite(buffer.data(),1,buffer.size(),stdout)!=buffer.size())throw std::runtime_error("Frame pipe closed");
        }
    } catch(const std::exception& error){std::fprintf(stderr,"%s\n",error.what());return 1;}
    return 0;
}
