#!/usr/bin/env python3
"""Eliminar todas las fotos y carpetas de Cloudinary bajo mapacu/ y borrar sus registros en la BD."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cloudinary
import cloudinary.api
import cloudinary.uploader
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.config import settings
from app.models.foto_espacio import FotoEspacio

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def public_id_from_url(url: str) -> str | None:
    if not url:
        return None
    partes = url.split('/')
    if len(partes) < 2:
        return None
    # Buscar la primera ocurrencia de 'mapacu' y tomar desde allí hasta el nombre del archivo
    if 'mapacu' not in partes:
        return None
    inicio = partes.index('mapacu')
    public_id = '/'.join(partes[inicio:])
    public_id = public_id.split('.')[0]
    return public_id


def destroy_public_id(public_id: str) -> bool:
    try:
        resultado = cloudinary.uploader.destroy(public_id)
        print(f"   ✅ Destroyed: {public_id} -> {resultado}")
        return True
    except Exception as exc:
        print(f"   ⚠️  Failed destroying {public_id}: {exc}")
        return False


def destroy_all_resources(prefix: str = 'mapacu/') -> None:
    print(f"🔍 Listando recursos Cloudinary con prefijo '{prefix}'...")
    next_cursor = None
    total = 0
    while True:
        params = {'type': 'upload', 'prefix': prefix, 'max_results': 500}
        if next_cursor:
            params['next_cursor'] = next_cursor
        response = cloudinary.api.resources(**params)
        resources = response.get('resources', [])
        for resource in resources:
            public_id = resource.get('public_id')
            if public_id:
                destroy_public_id(public_id)
                total += 1
        next_cursor = response.get('next_cursor')
        if not next_cursor:
            break
    print(f"✅ Recursos destruidos: {total}")


def delete_folder_recursive(folder_path: str) -> None:
    print(f"🧹 Eliminando carpeta vacía: {folder_path}")
    try:
        cloudinary.api.delete_folder(folder_path)
        print(f"   ✅ Carpeta eliminada: {folder_path}")
    except Exception as exc:
        print(f"   ⚠️  No se pudo eliminar carpeta {folder_path}: {exc}")


def cleanup_folders(prefix: str = 'mapacu') -> None:
    print(f"🔍 Eliminando carpetas bajo '{prefix}'...")
    try:
        folders = cloudinary.api.subfolders(prefix)
        for folder in folders.get('folders', []):
            path = folder.get('name')
            if path:
                delete_folder_recursive(path)
    except Exception as exc:
        print(f"   ⚠️  No se pudieron listar subcarpetas: {exc}")

    # Intentar eliminar la carpeta raíz si queda vacía
    delete_folder_recursive(prefix)


def cleanup_database() -> None:
    print("🗃️  Limpiando registros de fotos en la base de datos...")
    db = SessionLocal()
    try:
        fotos = db.query(FotoEspacio).all()
        count = len(fotos)
        for foto in fotos:
            print(f"   🗑️  Eliminando registro FotoEspacio ID {foto.id}")
            db.delete(foto)
        db.commit()
        print(f"✅ Registros eliminados: {count}")
    except Exception as exc:
        db.rollback()
        print(f"❌ Error limpiando BD: {exc}")
    finally:
        db.close()


def main():
    print("⚠️  ATENCIÓN: Esto eliminará TODAS las fotos y carpetas bajo mapacu/ en Cloudinary y sus registros en la BD.")
    confirm = input("Escribe 'SI' para confirmar: ")
    if confirm.strip().upper() != 'SI':
        print("Operación cancelada.")
        return

    destroy_all_resources('mapacu/')
    cleanup_folders('mapacu')
    cleanup_database()

    print("\n🎉 Limpieza completa. El sistema ha sido reiniciado.")


if __name__ == '__main__':
    main()
